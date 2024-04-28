class RunProject:
    def __init__(self, project):
        self.project = project
        self.project_id = project.get('_id')
        self.project_name = project.get('project_name')
        self.project_display_name = project.get('project_display_name')
        self.description = project.get('description')
        self.types = project.get('types')
        self.source_path = project.get('source_path')
        self.options = project.get('options')
        self.create_time = project.get('create_time')
        self.update_time = project.get('update_time')
        self.github_url = project.get('github_url')

    def run(self):
        print(f'Running project {self.project_name}')
