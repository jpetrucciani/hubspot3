repo = hubspot3
base_command = pytest
coverage = --cov-config setup.cfg --cov=$(repo)
html_report = --cov-report html
term_report = --cov-report term
xml_report = --cov-report xml
reports = $(html_report) $(term_report) $(xml_report)
target = --target-version py34
MAKEFLAGS = --silent --ignore-errors --no-print-directory


all: test_all

test_all:
	@$(base_command) $(coverage) $(reports) -s --pyargs $(repo)

check_format:
	@black $(target) --check $(repo)/

format:
	@black $(target) $(repo)/

.PHONY: test_all check_format format