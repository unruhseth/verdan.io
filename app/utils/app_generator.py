import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import os
import shutil

class AppGenerator:
    def __init__(self, config_path: str):
        """Initialize app generator with a YAML config file."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.template_env = Environment(
            loader=FileSystemLoader('app/utils/templates')
        )

    def _load_config(self):
        """Load app configuration from YAML file."""
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def generate_app(self):
        """Generate app files based on configuration."""
        app_name = self.config['app']['name']
        
        # Generate backend
        self._generate_backend(app_name)
        
        # Generate frontend
        self._generate_frontend(app_name)

    def _generate_backend(self, app_name):
        """Generate backend app files."""
        app_dir = Path(f'app/apps/{app_name}')

        # Create app directory structure
        os.makedirs(app_dir, exist_ok=True)
        os.makedirs(app_dir / 'tests', exist_ok=True)

        # Generate backend files from templates
        self._generate_models()
        self._generate_routes()
        self._generate_services()
        self._generate_tests()

    def _generate_frontend(self, app_name):
        """Generate frontend app files."""
        frontend_dir = Path(f'frontend/src/pages/apps/{app_name}')
        components_dir = Path(f'frontend/src/components/apps/{app_name}')
        styles_dir = Path(f'frontend/src/styles/apps')

        # Create frontend directory structure
        os.makedirs(frontend_dir, exist_ok=True)
        os.makedirs(components_dir, exist_ok=True)
        os.makedirs(styles_dir, exist_ok=True)

        # Generate frontend files
        self._generate_main_page(frontend_dir)
        self._generate_dashboard(frontend_dir)
        self._generate_settings(frontend_dir)
        self._generate_components(components_dir)
        self._generate_styles(styles_dir)
        self._update_app_registry()

    def _generate_main_page(self, frontend_dir):
        """Generate main app page."""
        template = self.template_env.get_template('frontend/MainPage.js.j2')
        content = template.render(
            app_name=self.config['app']['name'],
            app_title=self.config['app'].get('title', self.config['app']['name'].title()),
            models=self.config['app'].get('models', [])
        )
        with open(frontend_dir / f'{self.config["app"]["name"].title()}Page.js', 'w') as f:
            f.write(content)

    def _generate_dashboard(self, frontend_dir):
        """Generate app dashboard."""
        template = self.template_env.get_template('frontend/Dashboard.js.j2')
        content = template.render(
            app_name=self.config['app']['name'],
            models=self.config['app'].get('models', []),
            widgets=self.config['app'].get('dashboard', {}).get('widgets', [])
        )
        with open(frontend_dir / f'{self.config["app"]["name"].title()}Dashboard.js', 'w') as f:
            f.write(content)

    def _generate_settings(self, frontend_dir):
        """Generate app settings page."""
        template = self.template_env.get_template('frontend/Settings.js.j2')
        content = template.render(
            app_name=self.config['app']['name'],
            settings=self.config['app'].get('settings', [])
        )
        with open(frontend_dir / f'{self.config["app"]["name"].title()}Settings.js', 'w') as f:
            f.write(content)

    def _generate_components(self, components_dir):
        """Generate app-specific components."""
        for component in self.config['app'].get('components', []):
            template = self.template_env.get_template('frontend/Component.js.j2')
            content = template.render(
                app_name=self.config['app']['name'],
                component=component
            )
            with open(components_dir / f'{component["name"]}.js', 'w') as f:
                f.write(content)

    def _generate_styles(self, styles_dir):
        """Generate app-specific styles."""
        template = self.template_env.get_template('frontend/styles.css.j2')
        content = template.render(
            app_name=self.config['app']['name'],
            theme=self.config['app'].get('theme', {})
        )
        with open(styles_dir / f'{self.config["app"]["name"]}.css', 'w') as f:
            f.write(content)

    def _update_app_registry(self):
        """Update frontend app registry."""
        registry_path = Path('frontend/src/config/appRegistry.js')
        
        if not registry_path.exists():
            # Create new registry if it doesn't exist
            template = self.template_env.get_template('frontend/appRegistry.js.j2')
            content = template.render(apps=[self.config['app']])
        else:
            # Update existing registry
            with open(registry_path) as f:
                existing_content = f.read()
            
            # Parse existing content and add new app
            # This is a simplified version - you might want to use an AST parser
            template = self.template_env.get_template('frontend/appRegistryUpdate.js.j2')
            content = template.render(
                existing_content=existing_content,
                new_app=self.config['app']
            )
        
        with open(registry_path, 'w') as f:
            f.write(content)

    def _generate_models(self):
        """Generate models.py from configuration."""
        template = self.template_env.get_template('models.py.j2')
        models = self.config['app'].get('models', [])
        content = template.render(
            app_name=self.config['app']['name'],
            models=models
        )
        with open(f"app/apps/{self.config['app']['name']}/models.py", 'w') as f:
            f.write(content)

    def _generate_routes(self):
        """Generate routes.py from configuration."""
        template = self.template_env.get_template('routes.py.j2')
        endpoints = self.config['app'].get('endpoints', [])
        content = template.render(
            app_name=self.config['app']['name'],
            endpoints=endpoints
        )
        with open(f"app/apps/{self.config['app']['name']}/routes.py", 'w') as f:
            f.write(content)

    def _generate_services(self):
        """Generate services.py from configuration."""
        template = self.template_env.get_template('services.py.j2')
        models = self.config['app'].get('models', [])
        content = template.render(
            app_name=self.config['app']['name'],
            models=models
        )
        with open(f"app/apps/{self.config['app']['name']}/services.py", 'w') as f:
            f.write(content)

    def _generate_tests(self):
        """Generate test files from configuration."""
        test_templates = ['test_routes.py.j2', 'test_models.py.j2', 'test_services.py.j2']
        for template_name in test_templates:
            template = self.template_env.get_template(template_name)
            output_name = template_name.replace('.j2', '')
            content = template.render(
                app_name=self.config['app']['name'],
                models=self.config['app'].get('models', []),
                endpoints=self.config['app'].get('endpoints', [])
            )
            with open(f"app/apps/{self.config['app']['name']}/tests/{output_name}", 'w') as f:
                f.write(content) 