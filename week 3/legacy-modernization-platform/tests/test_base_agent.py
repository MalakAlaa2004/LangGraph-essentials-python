import os
from agents.base_agent import BaseDeepAgent
from agents.schemas.model_element import ModelElement


def test_git_storage_service_read_write(tmp_path):
    storage_dir = str(tmp_path)
    agent = BaseDeepAgent(agent_name="test_agent", base_storage_dir=storage_dir)

    element = ModelElement(
        id="comp-test",
        system_id="sys-test",
        layer="application",
        archimate_type="ApplicationComponent",
        name="TestComp",
        description="Test Application Component",
    )

    written_path = agent.storage_service.write_model_element(element)
    assert os.path.exists(written_path)

    read_elem = agent.storage_service.read_model_element(
        "sys-test", "application", "comp-test"
    )
    assert read_elem is not None
    assert read_elem.name == "TestComp"

    all_elems = agent.storage_service.list_model_elements("sys-test")
    assert len(all_elems) == 1


def test_base_agent_run():
    agent = BaseDeepAgent(agent_name="smoke_test", skill_name="archimate-metamodel")
    res = agent.run("List 3 elements in the Business Layer.")
    assert res is not None
    assert len(res) > 0
