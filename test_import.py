# TELEVIC CoCon CLIENT
# test_import.py
# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 3P Technologies Srl
# Author: Marco Miano
import cocon_client
from importlib import metadata

print("import ok")
try:
    print("dist version:", metadata.version("cocon_client"))
except metadata.PackageNotFoundError:
    print("version metadata not found (not installed?)")
