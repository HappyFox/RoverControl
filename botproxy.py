

class BotProxy(object):

  def __init__(self):
    self.planned_cmds = []  
    self.executed_cmds = []
    self.clients = []

  def cmd_count(self):
    return len(self.executed_cmds)
