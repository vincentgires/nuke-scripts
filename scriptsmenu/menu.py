import os
import nuke


def create_scripts_menus():
    scripts_path = os.environ.get('NUKE_SCRIPTS_PATH', '')
    files = [
        os.path.join(path, f)
        for path in scripts_path.split(os.pathsep)
        if os.path.isdir(path)
        for f in os.listdir(path)
        if f.endswith('.py')]

    if not files:
        return

    nuke_menu = nuke.menu('Nuke')
    scripts_menu = nuke_menu.addMenu('Scripts')

    def make_command(file_path):
        namespace = {
            '__name__': '__main__',
            '__file__': file_path,
            '__builtins__': __builtins__}

        def run():
            with open(file_path) as f:
                code = f.read()
            exec(code, namespace)
        return run

    for file_path in sorted(files):
        file, _ = os.path.splitext(os.path.basename(file_path))
        scripts_menu.addCommand(
            name=file.replace('_', ' ').title(),
            command=make_command(file_path))


if nuke.GUI:
    create_scripts_menus()
