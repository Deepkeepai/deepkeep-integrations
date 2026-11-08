import json
from pathlib import Path

import pytest
import yaml
from lupa.luajit21 import LuaRuntime


ROOT = Path(__file__).resolve().parents[1]
DECK = yaml.safe_load(
    (ROOT / "examples/deck/deepkeep-ai-guardrails.yaml").read_text(encoding="utf-8")
)
CONFIGS = [
    (f"admin-{mode}", json.loads(
        (ROOT / f"examples/admin-api/{mode}.json").read_text(encoding="utf-8")
    )["config"])
    for mode in ("input", "output")
] + [
    (f"deck-{plugin['config']['guarding_mode'].lower()}", plugin["config"])
    for plugin in DECK["plugins"]
]


@pytest.fixture(params=CONFIGS, ids=[name for name, _ in CONFIGS])
def config(request):
    return request.param


@pytest.fixture
def check(config):
    _, conf = config
    lua = LuaRuntime(unpack_returned_tuples=True)
    assert lua.eval("jit.version").startswith("LuaJIT 2.1")
    return lua, lua.execute(conf["functions"]["deepkeep_check"])


@pytest.mark.parametrize(
    "payload,blocked,reason",
    [
        ("{flagged=false}", False, ""),
        ('{flagged=false, verbosity="ignored"}', False, ""),
        ('{flagged=false, verbosity={{details={guardrail_action="block"}}}}', False, ""),
        ('{flagged=true, verbosity={{details={guardrail_action="alert"}}}}', False, "alert"),
        ('{flagged=true, verbosity={{details={guardrail_action="block"}}}}', True, "block"),
        ('{flagged=true, verbosity={{details={guardrail_action="redact"}}}}', True, "redact"),
        ('{flagged=true, verbosity={{details={guardrail_action="modify"}}}}', True, "modify"),
    ],
)
def test_policy(check, payload, blocked, reason):
    lua, function = check
    result = function(lua.eval(payload))
    assert result.block is blocked
    assert result.block_reason == reason
    assert result.masked is False
    assert isinstance(result.block_message, str)
    assert result.block_detail == ""


@pytest.mark.parametrize(
    "action",
    ['"unknown"', '""', '"ALERT"', '" alert "', "nil", "false", "true", "1", "{}"],
)
@pytest.mark.parametrize("with_alert", [False, True])
def test_invalid_actions_block(check, action, with_alert):
    lua, function = check
    alert = '{details={guardrail_action="alert"}},' if with_alert else ""
    payload = lua.eval(
        "{flagged=true, verbosity={" + alert
        + "{details={guardrail_action=" + action + "}}}}"
    )
    result = function(payload)
    assert result.block is True
    assert result.block_reason == "invalid_action"
    assert result.masked is False


@pytest.mark.parametrize(
    "payload",
    [
        "nil", "false", "true", "0", '"response"', "newproxy(true)", "{}",
        '{flagged="false"}', '{flagged="true"}', "{flagged=0}", "{flagged=1}",
        "{flagged={}}", "{flagged=newproxy(true)}", "{flagged=true}",
        "{flagged=true, verbosity=false}", "{flagged=true, verbosity=1}",
        '{flagged=true, verbosity="bad"}', "{flagged=true, verbosity={}}",
        "{flagged=true, verbosity=newproxy(true)}",
        "{flagged=true, verbosity={false}}", "{flagged=true, verbosity={1}}",
        '{flagged=true, verbosity={"bad"}}', "{flagged=true, verbosity={{}}}",
        "{flagged=true, verbosity={{details=false}}}",
        "{flagged=true, verbosity={{details=1}}}",
        '{flagged=true, verbosity={{details="bad"}}}',
        "{flagged=true, verbosity={{details=newproxy(true)}}}",
        '{flagged=true, verbosity={details={guardrail_action="alert"}}}',
        '{flagged=true, verbosity={[2]={details={guardrail_action="alert"}}}}',
        '{flagged=true, verbosity={{details={guardrail_action="alert"}}, [3]={}}}',
        '{flagged=true, verbosity={{details={guardrail_action="alert"}}, extra={}}}',
        '{flagged=true, verbosity={{details={guardrail_action="alert"}}, false}}',
        '{flagged=true, verbosity={false, {details={guardrail_action="alert"}}}}',
    ],
)
def test_malformed_responses_block_without_error(check, payload):
    lua, function = check
    result = function(lua.eval(payload))
    assert result.block is True
    assert result.block_reason == "invalid_response"
    assert result.masked is False
    assert result.block_detail == ""


@pytest.mark.parametrize("action", ["block", "redact", "modify", "unknown"])
@pytest.mark.parametrize(
    "construction",
    [
        "local items = {[1]=alert, [3]=alert, [5]=later}",
        "local items = {}; items[1]=alert; items[3]=alert; items[5]=later",
        "local items = {}; items[5]=later; items[3]=alert; items[1]=alert",
        "local items = {alert, nil, alert}; items[5]=later",
        "local items = {alert, alert, alert, alert, later}; items[2]=nil; items[4]=nil",
    ],
    ids=["literal", "ascending-inserts", "descending-inserts", "array-then-insert", "deleted-entries"],
)
def test_holes_cannot_hide_later_blocking_actions(check, action, construction):
    lua, function = check
    payload = lua.execute(
        'local alert = {details={guardrail_action="alert"}}\n'
        'local later = {details={guardrail_action="' + action + '"}}\n'
        + construction + "\nreturn {flagged=true, verbosity=items}"
    )
    result = function(payload)
    assert result.block is True
    assert result.block_reason == "invalid_response"
    assert result.masked is False
    assert result.block_detail == ""


@pytest.mark.parametrize(
    "actions,reason",
    [
        (("alert", "alert"), "alert"),
        (("alert", "block"), "block"),
        (("block", "alert"), "block"),
        (("alert", "redact"), "redact"),
        (("redact", "alert"), "redact"),
        (("alert", "modify"), "modify"),
        (("modify", "alert"), "modify"),
        (("modify", "redact", "block"), "block"),
        (("block", "redact", "modify"), "block"),
        (("alert", "unknown", "block"), "invalid_action"),
        (("block", "unknown", "alert"), "invalid_action"),
    ],
)
def test_multiple_actions(check, actions, reason):
    lua, function = check
    items = ",".join(
        '{guardrail_name="rule' + str(index) + '", details={guardrail_action="'
        + action + '"}}'
        for index, action in enumerate(actions)
    )
    result = function(lua.eval("{flagged=true, verbosity={" + items + "}}"))
    assert result.block is (reason != "alert")
    assert result.block_reason == reason
    assert result.block_detail == ", ".join(f"rule{i}" for i in range(len(actions)))
    assert result.masked is False


@pytest.mark.parametrize("name", ["nil", "false", "123", "{}", "newproxy(true)"])
def test_malformed_optional_name_does_not_error(check, name):
    lua, function = check
    result = function(lua.eval(
        "{flagged=true, verbosity={{guardrail_name=" + name
        + ', details={guardrail_action="alert"}}}}'
    ))
    assert result.block is False
    assert result.block_detail == ""
    assert result.masked is False


def test_configuration_contract(config):
    name, conf = config
    is_input = name.endswith("input")
    mode = "INPUT" if is_input else "OUTPUT"
    endpoint = "pre" if is_input else "post"
    field = "input" if is_input else "output"
    assert conf["guarding_mode"] == mode
    assert conf["text_source"] == (
        "concatenate_user_content" if is_input else "concatenate_all_content"
    )
    assert conf["allow_masking"] is False
    assert conf["request"] == {
        "url": f"$(conf.params.api_base)/api/v3/openai/moderations/{endpoint}",
        "headers": {"X-API-Key": "$(conf.params.api_key)"},
        "body": {
            "model": "$(conf.params.firewall_id)", field: "$(content)",
            "chat": "$(conf.params.chat_id)", "title": "$(conf.params.title)",
        },
    }
    assert conf["response"] == {
        "block": "$(deepkeep_check.block)",
        "block_message": "$(deepkeep_check.block_message)",
    }
    assert conf["metrics"] == {
        "block_reason": "$(deepkeep_check.block_reason)",
        "block_detail": "$(deepkeep_check.block_detail)",
        "masked": "$(deepkeep_check.masked)",
    }
    if name.startswith("deck"):
        assert conf["params"] == {
            key: '${{ env "DECK_DEEPKEEP_' + env + '" }}'
            for key, env in {
                "api_base": "API_BASE", "api_key": "API_KEY",
                "firewall_id": f"{mode}_FIREWALL_ID", "chat_id": "CHAT_ID", "title": "TITLE",
            }.items()
        }
    else:
        assert conf["params"] == {
            "api_base": "https://deepkeep.example.com", "api_key": "DEEPKEEP_API_KEY",
            "firewall_id": f"deepkeep-{field}-firewall", "chat_id": "", "title": "",
        }


@pytest.mark.parametrize("index", [0, 1], ids=["input", "output"])
def test_admin_and_deck_lua_match(index):
    assert CONFIGS[index][1]["functions"] == CONFIGS[index + 2][1]["functions"]
