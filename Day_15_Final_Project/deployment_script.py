#!/usr/bin/env python3
"""
Deployment Script - Day 15 Final Project
Handles packaging, deployment, and distribution of the entire project.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

import requests


class DeploymentManager:
    """
    Manages deployment and packaging of the Midnight Commits project.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.version = self._get_version()
        self.config = self._load_deployment_config()
        self.logger = self._setup_logger()

    def _get_version(self) -> str:
        """Extract version from main README or use current date."""
        readme_path = self.project_root / "main-README.md"
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                content = f.read()
                # Look for version in README
                for line in content.split('\n'):
                    if line.startswith("Version:"):
                        return line.split(":")[1].strip()

        # Fallback to date-based version
        return datetime.now().strftime("%Y.%m.%d")

    def _load_deployment_config(self) -> Dict:
        """Load deployment configuration."""
        config_path = self.project_root / "deployment.json"
        default_config = {
            "name": "midnight-commits",
            "version": self.version,
            "description": "24-day Python learning project",
            "author": "Midnight Commits",
            "python_requires": ">=3.8",
            "dependencies": [
                "requests",
                "beautifulsoup4",
                "pandas",
                "numpy",
                "scikit-learn",
                "matplotlib",
                "seaborn",
                "cryptography",
                "bcrypt",
                "argon2-cffi",
                "asyncio",
                "aiohttp",
                "selenium",
                "tkinter",
                "pillow"
            ],
            "exclude_patterns": [
                "*.pyc",
                "__pycache__",
                ".git",
                "*.log",
                "node_modules",
                "*.tmp"
            ],
            "platforms": ["linux", "windows", "macos"],
            "deployment_targets": ["pypi", "docker", "executable"]
        }

        if config_path.exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def _setup_logger(self):
        """Setup basic logging."""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger("DeploymentManager")

    def create_package(self, format_type: str = "zip", output_dir: Optional[Path] = None) -> Path:
        """
        Create a deployable package.

        Args:
            format_type: Package format (zip, tar.gz, tar.bz2)
            output_dir: Output directory for package

        Returns:
            Path to created package
        """
        if output_dir is None:
            output_dir = self.project_root / "dist"

        output_dir.mkdir(exist_ok=True)

        package_name = f"{self.config['name']}-{self.version}"
        package_path = output_dir / f"{package_name}.{format_type}"

        self.logger.info(f"Creating {format_type} package: {package_path}")

        # Collect files to include
        files_to_include = self._collect_project_files()

        if format_type == "zip":
            self._create_zip_package(package_path, files_to_include)
        elif format_type in ["tar.gz", "tar.bz2"]:
            self._create_tar_package(package_path, files_to_include, format_type)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

        self.logger.info(f"Package created successfully: {package_path}")
        return package_path

    def _collect_project_files(self) -> List[Path]:
        """Collect all project files to include in package."""
        files = []
        exclude_patterns = set(self.config['exclude_patterns'])

        for root, dirs, filenames in os.walk(self.project_root):
            root_path = Path(root)

            # Skip excluded directories
            dirs[:] = [d for d in dirs if not self._should_exclude(d, exclude_patterns)]

            for filename in filenames:
                if not self._should_exclude(filename, exclude_patterns):
                    files.append(root_path / filename)

        return files

    def _should_exclude(self, name: str, patterns: Set[str]) -> bool:
        """Check if file/directory should be excluded."""
        for pattern in patterns:
            if pattern.startswith("*"):
                if name.endswith(pattern[1:]):
                    return True
            elif pattern in name:
                return True
        return False

    def _create_zip_package(self, package_path: Path, files: List[Path]):
        """Create ZIP package."""
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in files:
                arcname = file_path.relative_to(self.project_root)
                zf.write(file_path, arcname)

    def _create_tar_package(self, package_path: Path, files: List[Path], format_type: str):
        """Create TAR package."""
        mode = 'w:gz' if format_type == 'tar.gz' else 'w:bz2'
        with tarfile.open(package_path, mode) as tf:
            for file_path in files:
                tf.add(file_path, arcname=file_path.relative_to(self.project_root))

    def create_requirements_file(self, output_path: Optional[Path] = None) -> Path:
        """
        Create requirements.txt file.

        Args:
            output_path: Path for requirements file

        Returns:
            Path to created requirements file
        """
        if output_path is None:
            output_path = self.project_root / "requirements.txt"

        self.logger.info(f"Creating requirements file: {output_path}")

        dependencies = self.config['dependencies']

        with open(output_path, 'w') as f:
            f.write("# Midnight Commits - Requirements\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
            for dep in dependencies:
                f.write(f"{dep}\n")

        return output_path

    def create_setup_py(self, output_path: Optional[Path] = None) -> Path:
        """
        Create setup.py file for PyPI distribution.

        Args:
            output_path: Path for setup.py file

        Returns:
            Path to created setup.py file
        """
        if output_path is None:
            output_path = self.project_root / "setup.py"

        self.logger.info(f"Creating setup.py file: {output_path}")

        setup_content = f'''"""
Setup script for Midnight Commits project.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="{self.config['name']}",
    version="{self.version}",
    author="{self.config['author']}",
    description="{self.config['description']}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/midnight-commits/midnight-commits",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Software Development",
    ],
    python_requires="{self.config['python_requires']}",
    install_requires={self.config['dependencies']},
    entry_points={{
        "console_scripts": [
            "midnight-commits=main:main",
        ],
    }},
    include_package_data=True,
    zip_safe=False,
)
'''

        with open(output_path, 'w') as f:
            f.write(setup_content)

        return output_path

    def create_dockerfile(self, output_path: Optional[Path] = None) -> Path:
        """
        Create Dockerfile for containerized deployment.

        Args:
            output_path: Path for Dockerfile

        Returns:
            Path to created Dockerfile
        """
        if output_path is None:
            output_path = self.project_root / "Dockerfile"

        self.logger.info(f"Creating Dockerfile: {output_path}")

        dockerfile_content = f'''# Midnight Commits - Docker Image
FROM python:{self.config['python_requires'].replace('>=', '')}-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libffi-dev \\
    libssl-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \\
    && chown -R app:app /app
USER app

# Expose port for web services
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "-m", "main"]
'''

        with open(output_path, 'w') as f:
            f.write(dockerfile_content)

        return output_path

    def build_executable(self, output_dir: Optional[Path] = None) -> Path:
        """
        Build standalone executable using PyInstaller.

        Args:
            output_dir: Output directory for executable

        Returns:
            Path to built executable
        """
        if output_dir is None:
            output_dir = self.project_root / "dist"

        output_dir.mkdir(exist_ok=True)

        self.logger.info("Building standalone executable with PyInstaller")

        try:
            # Check if PyInstaller is available
            subprocess.run([sys.executable, "-c", "import PyInstaller"],
                         check=True, capture_output=True)

        except subprocess.CalledProcessError:
            self.logger.error("PyInstaller not found. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"],
                         check=True)

        # Create spec file
        spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['{self.project_root}'],
    binaries=[],
    datas=[],
    hiddenimports={self.config['dependencies']},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='midnight-commits',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emojis=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''

        spec_path = self.project_root / "midnight-commits.spec"
        with open(spec_path, 'w') as f:
            f.write(spec_content)

        # Run PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", str(spec_path)]
        subprocess.run(cmd, cwd=self.project_root, check=True)

        # Move executable to dist directory
        exe_name = "midnight-commits" + (".exe" if os.name == 'nt' else "")
        exe_path = self.project_root / "dist" / exe_name

        if exe_path.exists():
            final_path = output_dir / exe_name
            shutil.move(str(exe_path), str(final_path))
            exe_path = final_path

        # Cleanup
        spec_path.unlink(missing_ok=True)
        build_dir = self.project_root / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir)

        self.logger.info(f"Executable built: {exe_path}")
        return exe_path

    def deploy_to_pypi(self, test: bool = True) -> bool:
        """
        Deploy package to PyPI.

        Args:
            test: Deploy to TestPyPI instead of production

        Returns:
            True if deployment successful
        """
        self.logger.info(f"Deploying to {'Test' if test else ''}PyPI")

        try:
            # Check if build tools are available
            subprocess.run([sys.executable, "-c", "import build"],
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self.logger.error("Build tools not found. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "build"],
                         check=True)

        try:
            # Check if twine is available
            subprocess.run([sys.executable, "-c", "import twine"],
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self.logger.error("Twine not found. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "twine"],
                         check=True)

        # Build distribution
        self.logger.info("Building distribution packages")
        subprocess.run([sys.executable, "-m", "build"], check=True)

        # Upload to PyPI
        repo_url = "--repository-url https://test.pypi.org/legacy/" if test else ""
        cmd = f"{sys.executable} -m twine upload {repo_url} dist/*"

        try:
            subprocess.run(cmd, shell=True, check=True)
            self.logger.info("Deployment to PyPI successful")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Deployment failed: {e}")
            return False

    def run_deployment_pipeline(self, targets: List[str]) -> Dict[str, bool]:
        """
        Run complete deployment pipeline.

        Args:
            targets: List of deployment targets

        Returns:
            Dict mapping targets to success status
        """
        results = {}

        # Create requirements.txt
        try:
            self.create_requirements_file()
            results['requirements'] = True
        except Exception as e:
            self.logger.error(f"Failed to create requirements.txt: {e}")
            results['requirements'] = False

        # Create setup.py
        try:
            self.create_setup_py()
            results['setup_py'] = True
        except Exception as e:
            self.logger.error(f"Failed to create setup.py: {e}")
            results['setup_py'] = False

        for target in targets:
            if target == "package":
                try:
                    self.create_package()
                    results['package'] = True
                except Exception as e:
                    self.logger.error(f"Package creation failed: {e}")
                    results['package'] = False

            elif target == "docker":
                try:
                    self.create_dockerfile()
                    results['docker'] = True
                except Exception as e:
                    self.logger.error(f"Dockerfile creation failed: {e}")
                    results['docker'] = False

            elif target == "executable":
                try:
                    self.build_executable()
                    results['executable'] = True
                except Exception as e:
                    self.logger.error(f"Executable build failed: {e}")
                    results['executable'] = False

            elif target == "pypi":
                results['pypi'] = self.deploy_to_pypi(test=True)

        return results


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Deployment Manager for Midnight Commits"
    )
    parser.add_argument(
        "action",
        choices=["package", "requirements", "setup", "docker", "executable", "pypi", "pipeline"],
        help="Deployment action to perform"
    )
    parser.add_argument(
        "--format",
        choices=["zip", "tar.gz", "tar.bz2"],
        default="zip",
        help="Package format"
    )
    parser.add_argument(
        "--output",
        help="Output directory"
    )
    parser.add_argument(
        "--targets",
        nargs="+",
        choices=["package", "docker", "executable", "pypi"],
        help="Deployment targets for pipeline"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory"
    )

    args = parser.parse_args()

    # Initialize deployment manager
    project_root = Path(args.project_root).resolve()
    deployer = DeploymentManager(project_root)

    try:
        if args.action == "package":
            package_path = deployer.create_package(args.format, Path(args.output) if args.output else None)
            print(f"✓ Package created: {package_path}")

        elif args.action == "requirements":
            req_path = deployer.create_requirements_file(Path(args.output) if args.output else None)
            print(f"✓ Requirements file created: {req_path}")

        elif args.action == "setup":
            setup_path = deployer.create_setup_py(Path(args.output) if args.output else None)
            print(f"✓ Setup.py created: {setup_path}")

        elif args.action == "docker":
            docker_path = deployer.create_dockerfile(Path(args.output) if args.output else None)
            print(f"✓ Dockerfile created: {docker_path}")

        elif args.action == "executable":
            exe_path = deployer.build_executable(Path(args.output) if args.output else None)
            print(f"✓ Executable built: {exe_path}")

        elif args.action == "pypi":
            success = deployer.deploy_to_pypi()
            if success:
                print("✓ Deployed to PyPI successfully")
            else:
                print("✗ PyPI deployment failed")
                sys.exit(1)

        elif args.action == "pipeline":
            if not args.targets:
                args.targets = ["package", "docker"]
            results = deployer.run_deployment_pipeline(args.targets)

            print("Deployment Pipeline Results:")
            for target, success in results.items():
                status = "✓" if success else "✗"
                print(f"  {status} {target}")

            failed = [k for k, v in results.items() if not v]
            if failed:
                print(f"\nFailed targets: {', '.join(failed)}")
                sys.exit(1)

    except Exception as e:
        print(f"✗ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()