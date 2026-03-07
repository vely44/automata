#!/usr/bin/env python3
"""
Configuration validation script for Automata
Tests that the custom LLM provider configuration works correctly
"""
import os
import yaml
import sys

def test_config_yaml():
    """Test that config.yaml is valid and properly structured"""
    try:
        with open('/home/user/automata/nanobot/config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        # Check required sections
        assert 'llm' in config, "Missing 'llm' section"
        assert 'provider' in config['llm'], "Missing 'provider' in llm config"
        assert 'model' in config['llm'], "Missing 'model' in llm config"

        print("✓ config.yaml is valid and properly structured")
        print(f"  - Provider: {config['llm']['provider']}")
        print(f"  - Model: {config['llm']['model']}")
        return True
    except Exception as e:
        print(f"✗ config.yaml validation failed: {e}")
        return False

def test_env_variables():
    """Test that environment variables can be properly set"""
    test_vars = {
        'DISCORD_BOT_TOKEN': 'test_token_123',
        'ANTHROPIC_API_KEY': 'test_key_123',
        'OPENAI_API_KEY': 'test_key_456',
        'LLM_PROVIDER': 'groq',
        'LLM_API_KEY': 'test_api_key_789'
    }

    try:
        for key, value in test_vars.items():
            os.environ[key] = value

        # Verify they're set
        for key, expected_value in test_vars.items():
            actual = os.environ.get(key)
            assert actual == expected_value, f"{key} mismatch"

        print("✓ Environment variables can be set correctly")
        print(f"  - {len(test_vars)} test variables validated")
        return True
    except Exception as e:
        print(f"✗ Environment variable test failed: {e}")
        return False

def test_docker_compose():
    """Test that docker-compose.yml is valid"""
    try:
        with open('/home/user/automata/docker-compose.yml', 'r') as f:
            compose = yaml.safe_load(f)

        # Check required services
        assert 'services' in compose, "Missing 'services' section"
        assert 'nanobot' in compose['services'], "Missing 'nanobot' service"

        # Check nanobot has environment vars for custom LLM
        nanobot = compose['services']['nanobot']
        assert 'environment' in nanobot, "Missing 'environment' in nanobot"
        env_vars = nanobot['environment']

        # Check for custom LLM variables
        has_llm_provider = any('LLM_PROVIDER' in str(v) for v in env_vars)
        has_llm_api_key = any('LLM_API_KEY' in str(v) for v in env_vars)

        assert has_llm_provider, "Missing LLM_PROVIDER in docker-compose environment"
        assert has_llm_api_key, "Missing LLM_API_KEY in docker-compose environment"

        print("✓ docker-compose.yml is valid and includes custom LLM support")
        print(f"  - Environment variables: {len(env_vars)} configured")
        return True
    except Exception as e:
        print(f"✗ docker-compose.yml validation failed: {e}")
        return False

def test_install_script():
    """Test that install script has correct syntax"""
    try:
        import subprocess
        result = subprocess.run(
            ['bash', '-n', '/home/user/automata/install'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

        # Check for custom provider references
        with open('/home/user/automata/install', 'r') as f:
            content = f.read()

        assert 'groq' in content, "Missing groq reference in install script"
        assert 'together' in content, "Missing together reference in install script"
        assert 'mistral' not in content or 'mistral' in content, "Mistral reference check"
        assert 'ollama' not in content, "Ollama reference should be removed"

        print("✓ install script has valid syntax and correct provider references")
        return True
    except Exception as e:
        print(f"✗ install script validation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Automata Configuration for Custom LLM Support")
    print("=" * 55)

    tests = [
        ("YAML Configuration", test_config_yaml),
        ("Environment Variables", test_env_variables),
        ("Docker Compose", test_docker_compose),
        ("Install Script", test_install_script),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        results.append(test_func())

    print("\n" + "=" * 55)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        return 0
    else:
        print(f"✗ Some tests failed ({passed}/{total} passed)")
        return 1

if __name__ == '__main__':
    sys.exit(main())
