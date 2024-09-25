from database import db

class Dieta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refeicao = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    data = db.Column(db.DateTime(), nullable=False)
    situacao = db.Column(db.Boolean(), nullable=False, default=False)
    user_id = db.Column(db.Integer, nullable=False)

    def to_dict(refeicao):
        if refeicao:
            return {
                "id": refeicao.id,
                "refeicao": refeicao.refeicao,
                "descricao": refeicao.descricao,
                "data": refeicao.data,
                "situacao": refeicao.situacao
            }
        
        return None