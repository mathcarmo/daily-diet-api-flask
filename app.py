from flask import Flask, jsonify, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import bcrypt
from database import db
from models.dieta import Dieta 
from models.user import User

app = Flask(__name__)
app.config['SECRET_KEY'] = "password"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/daily-diet'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Login realizado com sucesso!"})
    
    return jsonify({"message": "Credenciais inválidas"}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso!"})


@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt() )
        user = User(username=username, password=hashed_password, role='user')
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Usuário cadastrado com sucesso'})

    return jsonify({"message": "Dados inválidos"}), 400

#rota dieta

@app.route('/refeicao', methods=['POST'])
@login_required
def registrar_refeicao():
    data = request.json
    refeicao = data.get("refeicao")
    descricao = data.get("descricao")
    datain = data.get("datain")
    situacao = data.get("situacao")

    if refeicao and descricao and datain:
        if not situacao: 
            situacao = False

        refeicao = Dieta(refeicao=refeicao, descricao=descricao, data=datain, situacao=situacao, user_id=current_user.id)
        db.session.add(refeicao)
        db.session.commit()

        return jsonify({"message": "Refeição registrada com sucesso."})

    
    return jsonify({"message": "Dados inválidos. Refeição não registrada!"})

@app.route("/refeicao/<int:id_refeicao>", methods=["PUT"])
@login_required
def atualizar_refeicao(id_refeicao):
    
    refeicao_db = Dieta.query.get(id_refeicao)
    
    dados = request.json
    refeicao = dados.get("refeicao")
    descricao = dados.get("descricao")
    data = dados.get("data")
    situacao = dados.get("situacao")

    if refeicao_db:
        if current_user.id == refeicao_db.user_id:
            if refeicao_db and descricao and data:
                refeicao_db.refeicao = refeicao
                refeicao_db.descricao = descricao
                refeicao_db.data = data
                refeicao_db.situacao = situacao
                db.session.commit()
                return jsonify({"message": f"Refeição {id_refeicao} atualizada com sucesso."})
            
        return jsonify({"message": f"Não é possível alterar a refeição de outra pessoa."})
    
    return jsonify({"message": f"Refeição inexistente."})

# Apagar refeição
@app.route("/refeicao/<int:id_refeicao>", methods=["DELETE"])
@login_required
def deletar_refeicao(id_refeicao):
    refeicao = Dieta.query.get(id_refeicao)

    if refeicao:
        if current_user.id == refeicao.user_id:
            db.session.delete(refeicao)
            db.session.commit()
            return jsonify({"message": f"Refeição {id_refeicao} excluída com sucesso."})
        
        return jsonify({"message": f"Não é possível excluir a refeição de outra pessoa."})
    
    return jsonify({"message": f"Refeição {id_refeicao} inexistente."})

# Obter todas as refeições
@app.route("/refeicao", methods=["GET"])
@login_required
def listar_refeicao():
    refeicoes = Dieta.query.filter_by(user_id=current_user.id).order_by(Dieta.data)
    response = []
    if not refeicoes.first() == None:
        if refeicoes[0]:
            for refeicao in refeicoes:
                response.append(Dieta.to_dict(refeicao))

            return response
    
    return jsonify({"message": f"Nenhuma refeição cadastrada."})

# Obter uma refeição pelo id
@app.route("/refeicao/<int:id_refeicao>", methods=["GET"])
@login_required
def buscar_refeicao(id_refeicao):
    refeicao = Dieta.query.filter_by(id=id_refeicao, user_id=current_user.id).first()

    if not refeicao == None:
        return jsonify(Dieta.to_dict(refeicao))
    
    return jsonify({"message": f"Nenhuma refeição cadastrada."})


if __name__ == '__main__':
    app.run(debug=True)