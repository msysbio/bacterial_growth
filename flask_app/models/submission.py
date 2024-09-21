class Submission:
    def __init__(self, data, current_step):
        self.step = current_step or 1

        self.type         = data.get('type',         None)
        self.project_uuid = data.get('project_uuid', None)
        self.study_uuid   = data.get('study_uuid',   None)

        self.project = data.get('project', {'name': None, 'description': None})

    def _asdict(self):
        return {
            'type':         self.type,
            'project_uuid': self.project_uuid,
            'study_uuid':   self.study_uuid,
            'project':      self.project,
        }
