# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project

import json
import weakref
from enum import Enum

import jsonschema
import pytest
import regex as re
from pydantic import BaseModel

from vllm.distributed import cleanup_dist_env_and_memory
from vllm.entrypoints.llm import LLM
from vllm.outputs import RequestOutput
from vllm.sampling_params import GuidedDecodingParams, SamplingParams

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

# Separate backends which support grammars vs ones
# which only support regex based constraints in tests.
GRAMMAR_DECODING_BACKENDS = [
    # (backend, disable_any_whitespace),
    ("lm-format-enforcer", False),
    ("xgrammar", True),
    ("guidance", True),
]

ALL_DECODING_BACKENDS = ([("outlines", False)] + GRAMMAR_DECODING_BACKENDS)


@pytest.fixture(scope="module")
def llm():
    # pytest caches the fixture so we use weakref.proxy to
    # enable garbage collection
    llm = LLM(model=MODEL_NAME, max_model_len=1024, seed=0)

    with llm.deprecate_legacy_api():
        yield weakref.proxy(llm)
        del llm
    cleanup_dist_env_and_memory()


@pytest.mark.skip_global_cleanup
@pytest.mark.parametrize("guided_decoding_backend,disable_any_whitespace",
                         ALL_DECODING_BACKENDS)
def test_guided_regex(sample_regex, llm, guided_decoding_backend: str,
                      disable_any_whitespace: bool):
    sampling_params = SamplingParams(
        temperature=0.8,
        top_p=0.95,
        guided_decoding=GuidedDecodingParams(
            regex=sample_regex,
            backend=guided_decoding_backend,
            disable_any_whitespace=disable_any_whitespace))

    outputs = llm.generate(prompts=[
        f"Give an example IPv4 address with this regex: {sample_regex}"
    ] * 2,
                           sampling_params=sampling_params,
                           use_tqdm=True)

    assert outputs is not None
    for output in outputs:
        assert output is not None
        assert isinstance(output, RequestOutput)
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(generated_text)
        assert generated_text is not None
        assert re.fullmatch(sample_regex, generated_text) is not None
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")


@pytest.mark.skip_global_cleanup
@pytest.mark.parametrize("guided_decoding_backend,disable_any_whitespace",
                         ALL_DECODING_BACKENDS)
def test_guided_json_completion(sample_json_schema, llm,
                                guided_decoding_backend: str,
                                disable_any_whitespace: bool):
    sampling_params = SamplingParams(
        temperature=1.0,
        max_tokens=1000,
        guided_decoding=GuidedDecodingParams(
            json=sample_json_schema,
            backend=guided_decoding_backend,
            disable_any_whitespace=disable_any_whitespace))
    outputs = llm.generate(prompts=[
        f"Give an example JSON for an employee profile "
        f"that fits this schema: {sample_json_schema}"
    ] * 2,
                           sampling_params=sampling_params,
                           use_tqdm=True)

    assert outputs is not None

    for output in outputs:
        assert output is not None
        assert isinstance(output, RequestOutput)
        prompt = output.prompt

        generated_text = output.outputs[0].text
        assert generated_text is not None
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
        output_json = json.loads(generated_text)
        jsonschema.validate(instance=output_json, schema=sample_json_schema)


@pytest.mark.skip_global_cleanup
@pytest.mark.parametrize("guided_decoding_backend,disable_any_whitespace",
                         ALL_DECODING_BACKENDS)
def test_guided_complex_json_completion(sample_complex_json_schema, llm,
                                        guided_decoding_backend: str,
                                        disable_any_whitespace: bool):
    sampling_params = SamplingParams(
        temperature=1.0,
        max_tokens=1000,
        guided_decoding=GuidedDecodingParams(
            json=sample_complex_json_schema,
            backend=guided_decoding_backend,
            disable_any_whitespace=disable_any_whitespace))
    outputs = llm.generate(prompts=[
        f"Give an example JSON for an assignment grade "
        f"that fits this schema: {sample_complex_json_schema}"
    ] * 2,
                           sampling_params=sampling_params,
                           use_tqdm=True)

    assert outputs is not None

    for output in outputs:
        assert output is not None
        assert isinstance(output, RequestOutput)
        prompt = output.prompt

        generated_text = output.outputs[0].text
        assert generated_text is not None
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
        output_json = json.loads(generated_text)
        jsonschema.validate(instance=output_json,
                            schema=sample_complex_json_schema)


@pytest.mark.skip_global_cleanup
@pytest.mark.parametrize("guided_decoding_backend,disable_any_whitespace",
                         ALL_DECODING_BACKENDS)
def test_guided_definition_json_completion(sample_definition_json_schema, llm,
                                           guided_decoding_backend: str,
                                           disable_any_whitespace: bool):
    sampling_params = SamplingParams(
        temperature=1.0,
        max_tokens=1000,
        guided_decoding=GuidedDecodingParams(
            json=sample_definition_json_schema,
            backend=guided_decoding_backend,
            disable_any_whitespace=disable_any_whitespace))
    outputs = llm.generate(prompts=[
        f"Give an example JSON for solving 8x + 7 = -23 "
        f"that fits this schema: {sample_definition_json_schema}"
    ] * 2,
                           sampling_params=sampling_params,
                           use_tqdm=True)

    assert outputs is not None

    for output in outputs:
        assert output is not None
        assert isinstance(output, RequestOutput)
        prompt = output.prompt

        generated_text = output.outputs[0].text
        assert generated_text is not None
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
        output_json = json.loads(generated_text)
        jsonschema.validate(instance=output_json,
                            schema=sample_definition_json_schema)


@pytest.mark.skip_global_cleanup
@pytest.mark.parametrize("guided_decoding_backend,disable_any_whitespace",
                         ALL_DECODING_BACKENDS)
def test_guided_enum_json_completion(sample_enum_json_schema, llm,
                                     guided_decoding_backend: str,
                                     disable_any_whitespace: bool):
    sampling_params = SamplingParams(
        temperature=1.0,
        max_tokens=1000,
        guided_decoding=GuidedDecodingParams(
            json=sample_enum_json_schema,
            backend=guided_decoding_backend,
            disable_any_whitespace=disable_any_whitespace))
    outputs = llm.generate(prompts=[
        "Create a bug report JSON that fits this schema: "
        f"{sample_enum_json_schema}. Make it for a high priority critical bug."
    ] * 2,
                           sampling_params=sampling_params,
                           use_tqdm=True)

    assert outputs is not None

    for output in outputs:
        assert output is not None
        assert isinstance(output, RequestOutput)
        prompt = output.prompt

        generated_text = output.outputs[0].text
        assert generated_text is not None
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
        output_json = json.loads(generated_text)
        jsonschema.validate(instance=output_json,
                            schema=sample_enum_json_schema)

        # Additional assertions to verify enum values
        assert output_json["status"] in ["active", "inactive", "pending"]
        assert output_json["priority"] in ["low", "medium", "high", "critical"]
        assert output_json["category"]["type"] in [
            "bug", "feature", "improvement"
        ]
        assert output_json["category"]["severity"] in [1, 2, 3, 4, 5]
        for flag in output_json["flags"]:
            assert flag in ["urgent", "blocked", "needs_review", "approved"]


@pytest.mark.skip_global_cleanup
@pytest.mark.parametrize("guided_decoding_backend,disable_any_whitespace",
                         ALL_DECODING_BACKENDS)
def test_guided_choice_completion(sample_guided_choice, llm,
                                  guided_decoding_backend: str,
                                  disable_any_whitespace: bool):
    sampling_params = SamplingParams(
        temperature=0.8,
        top_p=0.95,
        guided_decoding=GuidedDecodingParams(
            choice=sample_guided_choice,
            backend=guided_decoding_backend,
            disable_any_whitespace=disable_any_whitespace))
    outputs = llm.generate(
        prompts="The best language for type-safe systems programming is ",
        sampling_params=sampling_params,
        use_tqdm=True)

    assert outputs is not None
    for output in outputs:
        assert output is not None
        assert isinstance(output, RequestOutput)
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(generated_text)
        assert generated_text is not None
        assert generated_text in sample_guided_choice
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")


@pytest.mark.skip_global_cleanup
@pytest.mark.parametrize("guided_decoding_backend,disable_any_whitespace",
                         GRAMMAR_DECODING_BACKENDS)
def test_guided_grammar(sample_sql_statements, llm,
                        guided_decoding_backend: str,
                        disable_any_whitespace: bool):
    sampling_params = SamplingParams(
        temperature=0.8,
        top_p=0.95,
        max_tokens=1000,
        guided_decoding=GuidedDecodingParams(
            grammar=sample_sql_statements,
            backend=guided_decoding_backend,
            disable_any_whitespace=disable_any_whitespace))
    outputs = llm.generate(
        prompts=("Generate a sql state that select col_1 from "
                 "table_1 where it is equals to 1"),
        sampling_params=sampling_params,
        use_tqdm=True,
    )

    assert outputs is not None
    for output in outputs:
        assert output is not None
        assert isinstance(output, RequestOutput)
        prompt = output.prompt

        generated_text = output.outputs[0].text
        assert generated_text is not None
        # use Lark to parse the output, and make sure it's a valid parse tree
        from lark import Lark
        parser = Lark(sample_sql_statements)
        parser.parse(generated_text)

        # remove spaces for comparison b/c we removed them in the grammar
        ground_truth = "SELECT col_1 from table_1 where col_1 = 1".replace(
            " ", "")

        assert generated_text.strip() == ground_truth

        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")


@pytest.mark.skip_global_cleanup
def test_guided_options_request_deprecation_warning(sample_regex, llm):
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

    with pytest.warns(DeprecationWarning, match="guided_options_request"):
        llm.generate(prompts="This should fail",
                     sampling_params=sampling_params,
                     use_tqdm=True,
                     guided_options_request=dict(guided_regex=sample_regex))


@pytest.mark.skip_global_cleanup
def test_validation_against_both_guided_decoding_options(sample_regex, llm):
    sampling_params = SamplingParams(
        temperature=0.8,
        top_p=0.95,
        guided_decoding=GuidedDecodingParams(regex=sample_regex))

    with pytest.raises(ValueError, match="Cannot set both"):
        llm.generate(prompts="This should fail",
                     sampling_params=sampling_params,
                     use_tqdm=True,
                     guided_options_request=dict(guided_regex=sample_regex))


@pytest.mark.skip_global_cleanup
def test_disable_guided_decoding_fallback(sample_regex, llm):
    # see has_xgrammar_unsupported_json_features()
    unsupported_json = {
        "type": "object",
        "properties": {
            "example": {
                "type": "string",
                "minLength": 5  # unsupported by xgrammar
            }
        }
    }
    sampling_params = SamplingParams(temperature=0.8,
                                     top_p=0.95,
                                     guided_decoding=GuidedDecodingParams(
                                         json=unsupported_json,
                                         backend="xgrammar",
                                         disable_fallback=True))

    with pytest.raises(
            ValueError,
            match="xgrammar does not support advanced JSON schema features "
            "like string length, item limits, or property bounds."):
        llm.generate(prompts="This should fail",
                     sampling_params=sampling_params,
                     use_tqdm=True)


@pytest.mark.skip_global_cleanup
@pytest.mark.parametrize("guided_decoding_backend,disable_any_whitespace",
                         GRAMMAR_DECODING_BACKENDS)
def test_guided_json_object(llm, guided_decoding_backend: str,
                            disable_any_whitespace: bool):
    sampling_params = SamplingParams(
        temperature=1.0,
        max_tokens=100,
        n=2,
        guided_decoding=GuidedDecodingParams(
            json_object=True,
            backend=guided_decoding_backend,
            disable_any_whitespace=disable_any_whitespace))

    outputs = llm.generate(
        prompts=("Generate a JSON object with curly braces for a person with "
                 "name and age fields for John Smith who is 31 years old."),
        sampling_params=sampling_params,
        use_tqdm=True)

    assert outputs is not None
    for output in outputs:
        assert output is not None
        assert isinstance(output, RequestOutput)

        for i in range(2):
            generated_text = output.outputs[i].text
            print(generated_text)
            assert generated_text is not None

            if disable_any_whitespace:
                assert "\n" not in generated_text

            # Parse to verify it is valid JSON
            parsed_json = json.loads(generated_text)
            # A list is not what was intended, but is still valid
            # json.
            assert isinstance(parsed_json, (dict, list))


class CarType(str, Enum):
    sedan = "sedan"
    suv = "SUV"
    truck = "Truck"
    coupe = "Coupe"


class CarDescription(BaseModel):
    brand: str
    model: str
    car_type: CarType


@pytest.mark.skip_global_cleanup
@pytest.mark.parametrize("guided_decoding_backend,disable_any_whitespace",
                         ALL_DECODING_BACKENDS)
def test_guided_json_completion_with_enum(llm, guided_decoding_backend: str,
                                          disable_any_whitespace: bool):
    json_schema = CarDescription.model_json_schema()
    sampling_params = SamplingParams(
        temperature=1.0,
        max_tokens=1000,
        guided_decoding=GuidedDecodingParams(
            json=json_schema,
            backend=guided_decoding_backend,
            disable_any_whitespace=disable_any_whitespace))
    outputs = llm.generate(
        prompts="Generate a JSON with the brand, model and car_type of"
        "the most iconic car from the 90's",
        sampling_params=sampling_params,
        use_tqdm=True)

    assert outputs is not None
    for output in outputs:
        assert output is not None
        assert isinstance(output, RequestOutput)
        prompt = output.prompt

        generated_text = output.outputs[0].text
        assert generated_text is not None
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
        output_json = json.loads(generated_text)
        jsonschema.validate(instance=output_json, schema=json_schema)


@pytest.mark.skip_global_cleanup
@pytest.mark.parametrize("guided_decoding_backend,disable_any_whitespace",
                         ALL_DECODING_BACKENDS)
def test_guided_number_range_json_completion(llm, guided_decoding_backend: str,
                                             disable_any_whitespace: bool):
    sample_output_schema = {
        "type": "object",
        "properties": {
            "age": {
                "type": "integer",
                "minimum": 18,
                "maximum": 99
            },
            "score": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 100.0
            },
            "zipcode": {
                "type": "string",
                "pattern": r"^\d{5}(-\d{4})?$"
            },
        },
        "required": ["age", "score", "zipcode"],
    }
    sampling_params = SamplingParams(
        temperature=1.0,
        max_tokens=1000,
        guided_decoding=GuidedDecodingParams(
            json=sample_output_schema,
            backend=guided_decoding_backend,
            disable_any_whitespace=disable_any_whitespace),
    )
    outputs = llm.generate(
        prompts=[
            "Create a JSON object for a user with age, score, and zipcode."
        ] * 2,
        sampling_params=sampling_params,
        use_tqdm=True,
    )

    assert outputs is not None

    for output in outputs:
        assert output is not None
        assert isinstance(output, RequestOutput)
        prompt = output.prompt

        generated_text = output.outputs[0].text
        assert generated_text is not None
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
        output_json = json.loads(generated_text)
        jsonschema.validate(instance=output_json, schema=sample_output_schema)
        assert 18 <= output_json["age"] <= 99
        assert 0.0 <= output_json["score"] <= 100.0
        assert (re.fullmatch(r"^\d{5}(-\d{4})?$", output_json["zipcode"])
                is not None)


@pytest.mark.skip_global_cleanup
def test_guidance_no_additional_properties(llm):
    schema = {
        'type': 'object',
        'properties': {
            'a1': {
                'type': 'string'
            },
            'a2': {
                'type': 'string'
            },
            'a3': {
                'type': 'string'
            }
        },
        'required': ['a1', 'a2', 'a3'],
    }

    prompt = (
        "<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a "
        "helpful assistant.<|im_end|>\n<|im_start|>user\nPlease generate a "
        "large JSON object with key-value pairs a1=b1, a2=b2, ..., a20=b20"
        "<|im_end|>\n<|im_start|>assistant\n")

    def generate_with_backend(backend, disable_additional_properties):
        guided_params = GuidedDecodingParams(
            json=schema,
            backend=backend,
            disable_any_whitespace=True,
            disable_additional_properties=disable_additional_properties)
        sampling_params = SamplingParams(temperature=0,
                                         max_tokens=256,
                                         guided_decoding=guided_params)

        outputs = llm.generate(prompts=prompt, sampling_params=sampling_params)
        assert outputs is not None
        generated_text = outputs[0].outputs[0].text
        assert generated_text is not None
        parsed_json = json.loads(generated_text)
        assert isinstance(parsed_json, dict)
        jsonschema.validate(instance=parsed_json, schema=schema)
        return parsed_json

    base_generated = generate_with_backend("guidance", False)
    assert "a1" in base_generated
    assert "a2" in base_generated
    assert "a3" in base_generated
    # by default additional keys are generated
    assert "a4" in base_generated
    assert "a5" in base_generated
    assert "a6" in base_generated

    generated = generate_with_backend("guidance", True)
    assert "a1" in generated
    assert "a2" in generated
    assert "a3" in generated
    assert "a4" not in generated
    assert "a5" not in generated
    assert "a6" not in generated
