import main

class General(Exception):
    def __init__(self, obj):
        main.logger.exception(f'General Exception: {obj}', exc_info=True)
        pass

class GameInitError(Exception):
    def __init__(self, obj):
        main.logger.exception(f'Game Initialization Exception: {obj}', exc_info=True)
        pass

class InputError(Exception):
    def __init__(self, obj):
        main.logger.exception(f'Input Error Exception: {obj}', exc_info=True)
        pass

class CodeSkillIssueError(Exception):
    def __init__(self, obj):
        main.logger.exception(f'Code Skill Issue Exception, Steven please check: {obj}', exc_info=True)
        pass

class ParserError(Exception):
    def __init__(self, obj):
        main.logger.error(f'Parsing error: {obj}', exc_info=True)
        pass