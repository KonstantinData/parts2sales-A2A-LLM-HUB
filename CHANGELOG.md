# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]
- Improve industry_class_agent: extract_industries now parses LLM output using
  `utils.json_safety.extract_json_array_from_response` for better resilience.
