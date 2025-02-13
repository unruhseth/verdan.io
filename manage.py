#!/usr/bin/env python
import click
import os
import shutil
import re
from pathlib import Path
from app.utils.app_generator import AppGenerator

@click.group()
def cli():
    """Verdan API management commands."""
    pass

@cli.command()
@click.option('--name', prompt='App name', help='Name of the new app')
@click.option('--config', help='Path to YAML config file')
@click.option('--interactive/--no-interactive', default=False, help='Run in interactive mode')
def create_app(name, config, interactive):
    """Create a new Verdan app from template or config."""
    if config:
        # Use YAML configuration
        generator = AppGenerator(config)
        generator.generate_app()
        click.echo(f"Successfully generated app '{name}' from configuration")
    else:
        # Use interactive or basic template
        app_dir = Path('app/apps')
        template_dir = app_dir / 'app_template'
        target_dir = app_dir / name

        if target_dir.exists():
            click.echo(f"Error: App directory {target_dir} already exists")
            return

        # Copy template directory
        shutil.copytree(template_dir, target_dir)

        # Get additional features if in interactive mode
        features = []
        if interactive:
            if click.confirm('Include authentication?', default=True):
                features.append('auth')
            if click.confirm('Generate CRUD endpoints?', default=True):
                features.append('crud')
            if click.confirm('Include test templates?', default=True):
                features.append('tests')
            if click.confirm('Generate frontend components?', default=True):
                features.append('frontend')

            # Get model information
            models = []
            while click.confirm('Add a model?', default=True):
                model_name = click.prompt('Model name')
                fields = []
                while click.confirm('Add a field?', default=True):
                    field = {
                        'name': click.prompt('Field name'),
                        'type': click.prompt('Field type', type=click.Choice([
                            'string', 'text', 'integer', 'float', 'boolean', 
                            'datetime', 'enum', 'json'
                        ])),
                        'nullable': click.confirm('Nullable?', default=False)
                    }
                    
                    if field['type'] == 'string':
                        field['length'] = click.prompt('String length', type=int, default=255)
                    elif field['type'] == 'enum':
                        values = []
                        while click.confirm('Add enum value?', default=True):
                            values.append(click.prompt('Value'))
                        field['values'] = values
                    elif field['type'] == 'boolean':
                        field['default'] = click.confirm('Default value', default=False)
                    
                    fields.append(field)
                
                models.append({
                    'name': model_name,
                    'fields': fields
                })

            # Generate YAML config
            config = {
                'app': {
                    'name': name,
                    'title': click.prompt('App title', default=name.title()),
                    'description': click.prompt('App description'),
                    'pricing': {
                        'monthly': click.prompt('Monthly price', type=float, default=0),
                        'yearly': click.prompt('Yearly price', type=float, default=0)
                    },
                    'models': models,
                    'frontend': {
                        'theme': {
                            'primary_color': click.prompt('Primary color', default='#1890ff'),
                            'secondary_color': click.prompt('Secondary color', default='#52c41a')
                        }
                    }
                }
            }

            # Save config for future reference
            os.makedirs('examples', exist_ok=True)
            import yaml
            with open(f'examples/{name}_app.yaml', 'w') as f:
                yaml.dump(config, f)

            # Use the config to generate the app
            generator = AppGenerator(f'examples/{name}_app.yaml')
            generator.generate_app()
        else:
            # Basic template generation
            for root, _, files in os.walk(target_dir):
                for file in files:
                    if file.endswith(('.py', '.md')):
                        file_path = Path(root) / file
                        with open(file_path) as f:
                            content = f.read()

                        # Replace app name placeholders
                        content = content.replace('app_name', name)
                        content = content.replace('app_template', name)
                        content = content.replace('AppName', ''.join(word.capitalize() for word in name.split('_')))

                        with open(file_path, 'w') as f:
                            f.write(content)

        click.echo(f"Successfully created app '{name}'")
        click.echo("\nNext steps:")
        click.echo(f"1. Register the blueprint in app/__init__.py")
        click.echo(f"2. Update the models in {name}/models.py")
        click.echo(f"3. Add your routes in {name}/routes.py")
        click.echo(f"4. Write your business logic in {name}/services.py")
        if 'frontend' in features:
            click.echo(f"5. Check the generated frontend components in frontend/src/pages/apps/{name}")
            click.echo(f"6. Customize the UI components as needed")

@cli.command()
@click.argument('app_name')
def generate_crud(app_name):
    """Generate CRUD endpoints for an existing app."""
    app_dir = Path(f'app/apps/{app_name}')
    if not app_dir.exists():
        click.echo(f"Error: App directory {app_dir} does not exist")
        return

    # Add CRUD route templates
    routes_file = app_dir / 'routes.py'
    with open(routes_file, 'a') as f:
        f.write(f"""

# CRUD Routes
@{app_name}_bp.route("/", methods=["GET"])
def list_items():
    \"\"\"List all items\"\"\"
    try:
        items = YourModel.query.all()
        return jsonify([item.to_dict() for item in items]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@{app_name}_bp.route("/<int:item_id>", methods=["GET"])
def get_item(item_id):
    \"\"\"Get a specific item\"\"\"
    try:
        item = YourModel.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(item.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@{app_name}_bp.route("/", methods=["POST"])
def create_item():
    \"\"\"Create a new item\"\"\"
    try:
        data = request.json
        item = YourModel(**data)
        db.session.add(item)
        db.session.commit()
        return jsonify(item.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@{app_name}_bp.route("/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    \"\"\"Update an item\"\"\"
    try:
        item = YourModel.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        data = request.json
        for key, value in data.items():
            setattr(item, key, value)
        db.session.commit()
        return jsonify(item.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@{app_name}_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    \"\"\"Delete an item\"\"\"
    try:
        item = YourModel.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
""")

    click.echo(f"Generated CRUD endpoints in {routes_file}")
    click.echo("Remember to:")
    click.echo("1. Replace 'YourModel' with your actual model class")
    click.echo("2. Add any necessary authentication decorators")
    click.echo("3. Customize the endpoints as needed")

if __name__ == '__main__':
    cli() 