from app import create_app
from models import db, Service

app = create_app("stream_tracker_db", testing = False)

db.drop_all()
db.create_all()

amazon = Service(name="Amazon Prime Video", image_url="https://image.tmdb.org/t/p/original/dQeAar5H991VYporEjUspolDarG.jpg")
netflix = Service(name="Netflix", image_url="https://image.tmdb.org/t/p/original/pbpMk2JmcoNnQwx5JGpXngfoWtp.jpg")
disney = Service(name="Disney Plus", image_url="https://image.tmdb.org/t/p/original/97yvRBw1GzX7fXprcF80er19ot.jpg")
hbo = Service(name="HBO Max", image_url="https://image.tmdb.org/t/p/original/fksCUZ9QDWZMUwL2LgMtLckROUN.jpg")
hulu = Service(name="Hulu", image_url="https://image.tmdb.org/t/p/original/bxBlRPEPpMVDc4jMhSrTf2339DW.jpg")
peacock = Service(name="Peacock Premium", image_url="https://image.tmdb.org/t/p/original/2aGrp1xw3qhwCYvNGAJZPdjfeeX.jpg")
paramount = Service(name="Paramount Plus", image_url="https://image.tmdb.org/t/p/original/h5DcR0J2EESLitnhR8xLG1QymTE.jpg")
starz = Service(name="Starz", image_url="https://image.tmdb.org/t/p/original/yIKwylTLP1u8gl84Is7FItpYLGL.jpg")
showtime = Service(name="Showtime", image_url="https://image.tmdb.org/t/p/original/kkUHFtdjasnnOknZN69TbZ2fCTh.jpg")
apple = Service(name="Apple TV Plus", image_url="https://image.tmdb.org/t/p/original/2E03IAZsX4ZaUqM7tXlctEPMGWS.jpg")

db.session.add_all([amazon, netflix, disney, hbo, hulu, peacock, paramount, starz, showtime, apple])
db.session.commit()