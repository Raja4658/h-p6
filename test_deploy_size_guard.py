from pathlib import Path


def test_deploy_dependencies_are_lightweight():
    req_text = Path('requirements.txt').read_text(encoding='utf-8')
    heavy_packages = [
        'torch',
        'transformers',
        'sentence-transformers',
        'huggingface-hub',
        'scikit-learn',
        'numpy',
    ]

    for pkg in heavy_packages:
        assert pkg not in req_text.lower(), (
            f'{pkg} is too heavy for Vercel serverless deployment; '
            'replace it with a lightweight implementation.'
        )
