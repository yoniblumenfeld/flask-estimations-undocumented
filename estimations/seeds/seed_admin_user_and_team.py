from estimations.models import Questionnaire,Question,Soldier,Team
from estimations import app,db

def seed_team(teamname):
    t = Team(teamname=teamname)
    db.session.add(t)
    db.session.commit()


def seed_soldier(username,military_id,level,teamname):
    s = Soldier(username=username,military_id=military_id)
    t = Team.query.filter_by(teamname=teamname).first()
    s.level = level
    s.team = t
    db.session.add(s)
    db.session.add(t)
    db.session.commit()

if __name__ == "__main__":
    seed_team("Admins")
    seed_team("Rookies")
    seed_soldier("soldier1",2222222,1,"Admins")
    seed_soldier("soldier2",1111111,0,"Rookies")

