import os
import sys
import importlib.util
from skills.skill_api import SKILLS_DIR

_loaded_skills = {}

def ensure_skills_dir():
    if not os.path.exists(SKILLS_DIR):
        os.makedirs(SKILLS_DIR)

def discover_skills():
    ensure_skills_dir()
    skills = []
    for filename in sorted(os.listdir(SKILLS_DIR)):
        if filename.endswith('.py') and not filename.startswith('_'):
            skill_name = filename[:-3]
            filepath = os.path.join(SKILLS_DIR, filename)
            mtime = os.path.getmtime(filepath)
            skills.append((skill_name, filepath, mtime))
    return skills

def load_skill_from_path(skill_name, filepath):
    spec = importlib.util.spec_from_file_location(skill_name, filepath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[skill_name] = mod
    spec.loader.exec_module(mod)
    return mod

def load_skills(assistant):
    global _loaded_skills
    ensure_skills_dir()
    count = 0
    for skill_name, filepath, _ in discover_skills():
        try:
            mod = load_skill_from_path(skill_name, filepath)
            metadata = getattr(mod, 'metadata', {})
            meta_name = metadata.get('name', skill_name)

            if hasattr(mod, 'register'):
                mod.register(assistant)
                _loaded_skills[skill_name] = {'module': mod, 'filepath': filepath}
                count += 1
                print(f"Loaded skill: {meta_name} ({skill_name})")
            else:
                print(f"Skill '{filename}' has no register() function — skipping")
        except Exception as e:
            print(f"Error loading skill {skill_name}: {e}")
    if count:
        print(f"Total: {count} external skill(s) loaded")
    return count

def reload_skill(assistant, skill_name):
    if skill_name in _loaded_skills:
        info = _loaded_skills[skill_name]
        filepath = info['filepath']
        try:
            mod = load_skill_from_path(skill_name, filepath)
            if hasattr(mod, 'register'):
                mod.register(assistant)
                _loaded_skills[skill_name]['module'] = mod
                print(f"Reloaded skill: {skill_name}")
                return True
        except Exception as e:
            print(f"Error reloading skill {skill_name}: {e}")
    return False

def list_skills():
    ensure_skills_dir()
    result = []
    for skill_name, filepath, _ in discover_skills():
        try:
            mod = load_skill_from_path(skill_name, filepath)
            metadata = getattr(mod, 'metadata', {})
            result.append({
                'name': metadata.get('name', skill_name),
                'version': metadata.get('version', '?'),
                'author': metadata.get('author', '?'),
                'description': metadata.get('description', ''),
                'skill_name': skill_name,
                'loaded': skill_name in _loaded_skills
            })
        except Exception as e:
            result.append({
                'name': skill_name,
                'version': '?',
                'author': '?',
                'description': f'Error: {e}',
                'skill_name': skill_name,
                'loaded': False
            })
    return result
