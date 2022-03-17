"""
Copyright 2019 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


from __future__ import absolute_import
import os
import nox

BLACK_PATHS = ["google", "tests"]

if os.path.exists("samples"):
    BLACK_PATHS.append("samples")


@nox.session
def lint(session):
    """Run linters.
    Returns a failure if the linters find linting errors or sufficiently
    serious code quality issues.
    """
    session.install(
        "flake8==4.0.1",
        "flake8-annotations==2.7.0",
        "black==21.12b0",
        "mypy==0.910",
        "sqlalchemy-stubs==0.4",
        "types-pkg-resources==0.1.3",
        "types-PyMySQL==1.0.6",
        "types-mock==4.0.5",
        "twine==3.7.1",
    )
    session.install("-r", "requirements.txt")
    session.run("black", "--check", *BLACK_PATHS)
    session.run("flake8", "google", "tests")
    session.run("mypy", "google", "tests")
    session.run("python", "setup.py", "sdist")
    session.run("twine", "check", "dist/*")


@nox.session
def blacken(session):
    """Run black.
    Format code to uniform standard.
    This currently uses Python 3.6 due to the automated Kokoro run of synthtool.
    That run uses an image that doesn't have 3.6 installed. Before updating this
    check the state of the `gcp_ubuntu_config` we use for that Kokoro run.
    """
    session.install("black==21.12b0")
    session.run("black", *BLACK_PATHS)


def default(session, path):
    # Install all test dependencies, then install this package in-place.
    session.install("-r", "requirements-test.txt")
    session.install("-e", ".")
    session.install("-r", "requirements.txt")
    # Run py.test against the unit tests.
    session.run(
        "py.test",
        "--cov=google/cloud/sql/connector",
        "-v",
        "--cov-config=.coveragerc",
        "--cov-report=",
        "--cov-fail-under=0",
        path,
        *session.posargs,
    )


@nox.session(python=["3.7", "3.8", "3.9", "3.10"])
def unit(session):
    default(session, os.path.join("tests", "unit"))


@nox.session(python=["3.7", "3.8", "3.9", "3.10"])
def system(session):
    default(session, os.path.join("tests", "system"))


@nox.session(python=["3.7", "3.8", "3.9", "3.10"])
def test(session):
    default(session, os.path.join("tests", "unit"))
    default(session, os.path.join("tests", "system"))
