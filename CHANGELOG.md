# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]
- Improve industry_class_agent: extract_industries now parses LLM output using
  `utils.json_safety.extract_json_array_from_response` for better resilience.
- Enhance `extract_json_array_from_response` to locate arrays with regex and
  provide clearer errors when no array is present.
- Update company_match_agent to parse LLM output with
  `extract_json_array_from_response`, preventing JSONDecodeError on noisy replies.
