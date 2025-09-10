# Contributing

Thanks for taking the time to contribute to **cocon_client**!

## Development setup

1. Fork the repository and clone your fork.
2. Create and activate a Python 3.11+ virtual environment.
3. Install the project in editable mode:

   ```bash
   pip install -e .
   ```

4. Before committing, ensure the code still parses:

   ```bash
   python -m py_compile $(git ls-files '*.py')
   ```

## Adding new models to `parser.py`

The client parses notification payloads into typed dataclasses defined in
[`parser.py`](./cocon_client/parser.py). To add support for a new model:

1. **Create a dataclass** that represents the payload structure.
2. **Register the dataclass** with the JSON key returned by the server using the
   `@register_model("YourKey")` decorator.
3. If the payload needs special handling, implement a `from_dict` classmethod
   that converts the raw dictionary into the dataclass.
4. **Expose the model** in `cocon_client/__init__.py` by importing it and
   adding it to `__all__` so it is available to users of the package.
5. Update documentation and examples as appropriate.

## Licensing and contributor terms

This project uses a **dual-license model**:

- **LGPL-3.0-or-later** for open-source use.
- **Commercial license** available from the copyright holder for organizations that cannot, or prefer not to, comply with LGPL terms.

By submitting a contribution (code, docs, or other assets), you agree that:

1. **Dual licensing of contributions**  
   You grant the copyright holder a perpetual, worldwide, non-exclusive license
   to distribute your contribution under:
   - the **GNU Lesser General Public License v3.0 or later (LGPL-3.0-or-later)**, **and**
   - a **separate commercial license** granted by the copyright holder.

2. **No additional restrictions**  
   You will not add terms that conflict with the dual-licensing model (e.g., “GPL-only” restrictions or third-party terms that prevent commercial relicensing).

3. **Certification of origin**  
   You certify that the contribution is your original work (or you have the right to submit it), and that you have the authority to grant the above licenses.

## Developer Certificate of Origin (DCO)

All commits must be signed off to indicate agreement with the DCO.

Add a “Signed-off-by” line to each commit message:

```
Signed-off-by: Your Name <you@example.com>
```

You can configure Git to add this automatically with `-s`:

```bash
git commit -s -m "Your commit message"
```

Ensure your Git identity is set correctly:

```bash
git config user.name "Your Name"
git config user.email "you@example.com"
```

## Submitting changes

- Keep commits focused and include descriptive messages.
- Ensure documentation is updated for any new features.
- Open a pull request against the `main` branch and describe your changes and how to test them.
- By opening a PR, you acknowledge the **Licensing and contributor terms** and the **DCO** above.

## Contact for commercial licensing

For commercial licensing (closed-source usage, private modifications, support, warranties, or tailored terms), contact:

- **3P Technologies S.r.l.**  
- **contact@trepi.it / www.trepi.it**

Happy hacking!