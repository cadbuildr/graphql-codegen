"""Command-line interface for GraphQL Codegen."""

import click
from pathlib import Path
from .generator import generate_from_directory


@click.command()
@click.argument(
    "schema_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--stdout", is_flag=True, help="Output to stdout instead of files")
@click.option("--flat", is_flag=True, help="Generate single file instead of package structure")
def main(schema_dir: Path, verbose: bool, stdout: bool, flat: bool):
    """Generate Python code from GraphQL schema directory.

    SCHEMA_DIR should contain schema.graphql and codegen.yaml files.
    
    Use --stdout to output code to stdout instead of creating files.
    Use --flat to generate a single file instead of package structure.
    """
    try:
        if verbose:
            click.echo(f"Processing schema directory: {schema_dir}")

        # Override config with CLI options
        from .config import load_config
        config = load_config(schema_dir)
        
        if stdout:
            config.stdout = True
        if flat:
            config.flat_output = True

        result = generate_from_directory(schema_dir, verbose=verbose, override_config=config)

        if result.success:
            if not stdout:
                click.echo(
                    f"✅ Generated package '{result.package_name}' at: {result.output_path}"
                )
        else:
            click.echo(f"❌ Generation failed: {result.error}", err=True)
            raise click.ClickException(result.error)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.ClickException(str(e))


if __name__ == "__main__":
    main()
