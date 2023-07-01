from flask import Flask, render_template, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates')

app = Flask(__name__)
cors = CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Fleming-Case-Study'

db = SQLAlchemy(app)

migrate = Migrate(app, db)

# login_manager = LoginManager(app)
# login_manager.login_view = 'login'
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120))

    def __init__(self, name, email, password, role):
        self.name = name
        self.email = email
        self.password = password
        self.role = role

class Create_offers(db.Model):
    offer_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer)

    def __init__(self,title, description, price, password, user_id):
        self.title = title
        self.description = description
        self.price = price
        self.password = password
        self.user_id = user_id

class Bid(db.Model):
    bid_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), nullable = False)
    password = db.Column(db.String(120), nullable = False)
    price = db.Column(db.Integer, nullable = True)
    offer_id = db.Column(db.Integer, db.ForeignKey("create_offers.offer_id"), nullable=False)
    
    def __init__(self,name, password, price, offer_id):
        self.name = name
        self.password = password
        self.price = price
        self.offer_id = offer_id


@app.route('/', methods = ['GET','POST'])
def home(): 
    if request.method == 'POST':
        # Logic for handling the POST request
        return 'Handle closeoffers POST request'
    else:
        # Logic for handling the GET request
        return render_template('home.html')   

@app.route('/register', methods=['GET','POST'])
def register():
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = generate_password_hash(request.form.get('password'), method='sha256')
            role = request.form.get('role')

            # Check if user already exists
            if User.query.filter_by(email=email).first():
                flash('Email address already exists')

            newuser = User(name=name, email=email,password=password, role=role)
            db.session.add(newuser)
            db.session.commit()
            return render_template('login.html')
        return render_template('register.html')
    except Exception as e:
        return jsonify({'Error': str(e)})
  
@ app.route('/login', methods=['GET', 'POST'])
def login():
    try: 
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            newuser = User.query.filter_by(email=email).first()

            if newuser and check_password_hash(newuser.password, password):
                print("Login Successful", newuser.role)
                return jsonify({'role': newuser.role, 'userid': newuser.id})  
                
            else: 
                print("Invalid User")

                
        return render_template('login.html')
    
    except Exception as e:
        return jsonify({'Error': str(e)})
    
@app.route('/createoffers', methods=['GET', 'POST'])
def createoffers():
    try:
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            password = generate_password_hash(request.form.get('password'), method='sha256')
            price = request.form.get('price')
            user_id = request.form.get('userid')

            newoffer = Create_offers(title=title, description=description, price=price, password=password, user_id=user_id )
            db.session.add(newoffer)
            db.session.commit()
            return 'offer created successfully'
        
        return render_template('create_offers.html')
    except Exception as e:
        return jsonify({'Error': str(e)})


@app.route('/listoffers', methods=['GET','POST'])
def listoffers():
    try: 
        if request.method == 'GET':
            offers = Create_offers.query.all()
            data = []

            for offer in offers:
                offer_data = {
                    'offer_id': offer.offer_id,
                    'title': offer.title,
                    'description': offer.description,
                    'price': offer.price,
                    'user_id': offer.user_id,
                }
                data.append(offer_data)

            if 'application/json' in request.headers.get('Accept', ''):
                return jsonify(data)
            else:
                return render_template('list_offers.html', offers=data)

    except Exception as e:
        return jsonify({'Error': str(e)})


@app.route('/createbid', methods =['GET','POST'])
def createbid():
    try: 
        if request.method == 'POST':
            offer_id = request.form.get('offer_id')
            name = request.form.get('name')
            password = generate_password_hash(request.form.get('bidpassword'), method='sha256')
            price = request.form.get('amount')

            new_bid = Bid(offer_id=offer_id, name=name, password=password,price=price)
            db.session.add(new_bid)
            db.session.commit()
            return 'bid successfully created'
        
        return render_template('bid.html')
    
    except Exception as e: 
        return jsonify({'Error': str(e)})
    

@app.route('/deletebid', methods = ['POST','GET'])
def deletebid():
    try:
        if request.method == 'POST':
            name = request.form.get("bid_name")
            password = request.form.get("password")

            deletebid = Bid.query.filter_by(name=name).first()

            if deletebid and check_password_hash(deletebid.password, password):
                db.session.delete(deletebid)
                db.session.commit()
                return "bid successfullt deleted"
            return 'wrong password'
        else: 
            return render_template('deletebid.html')
    
    except Exception as e:
        return jsonify({'Error': str(e)})



@app.route('/myoffers', methods=['GET', 'POST'])
def myoffers():
    try:
            user_id = request.form.get('userId')
            # print(user_id)  

            myoffer = Create_offers.query.filter_by(user_id=user_id)
            # print(myoffer)  
            data = []

            for offer in myoffer:
                my_data = {
                    'offer_id': offer.offer_id,
                    'title': offer.title,
                    'description': offer.description,
                    'price': offer.price,
                    'user_id': offer.user_id,
                }
                data.append(my_data)    

            # print(data)
            if 'application/json' in request.headers.get('Accept', ''):
                return jsonify(data)
            else:
                return render_template('myoffer.html', offers=data)

        # elif request.method == 'GET':
        #     user_id = request.args.get('userId') 

        #     myoffer = Create_offers.query.filter_by(user_id=user_id)
        #     data = []

        #     for offer in myoffer:
        #         my_data = {
        #             'offer_id': offer.offer_id,
        #             'title': offer.title,
        #             'description': offer.description,
        #             'price': offer.price,
        #             'user_id': offer.user_id,
        #         }
        #         data.append(my_data)

        #     if 'application/json' in request.headers.get('Accept', ''):
        #         return jsonify(data)
        #     else:
        #         return render_template('myoffer.html', offers=data)

    except Exception as e:
        return jsonify({'Error': str(e)})

@app.route('/bidforoffer', methods=['GET', 'POST'])
def bidforoffer():
    try:
        offer_id = request.form.get('offer_id')
        print(offer_id)  

        mybid = Bid.query.filter_by(offer_id=offer_id)
        # print(mybid)  
        data = []

        for bid in mybid:
            my_data = {
                'name': bid.name,
                'price': bid.price,
            }
            data.append(my_data)    

        print(data)
        if 'application/json' in request.headers.get('Accept', ''):
            return jsonify(data)
        else:
            return render_template('mybid.html', offers=data)
        
    except Exception as e: 
        return jsonify({'Error': str(e)})

@app.route('/finalizebid', methods=['GET', 'POST'])
def finalizebid():
    try:
        return render_template('finalize.html')
    except Exception as e: 
        return jsonify({'Error': str(e)})


@app.route('/closeoffers', methods=['GET', 'POST'])
def closeoffers():
    try:
        # if request.session == 'POST':
        offer_id = request.form.get('offer_id')
        user_id = request.form.get('user_id')
        print(offer_id)
        print(user_id)

        offer = Create_offers.query.filter_by(user_id=user_id)
        # print(offer)
        bid = Bid.query.filter_by(offer_id=offer_id)
        # print(bid)

        for offers in offer: 
            db.session.delete(offers)

        for bids in bid:
            db.session.delete(bids)
        
        db.session.commit()
        return jsonify({'message': 'Offer and bid successfully deleted'})

    
    except Exception as e: 
        return jsonify({'Error': str(e)})



if __name__ == '__main__':
    from flask_cors import CORS
    CORS(app)
    with app.app_context():
        db.create_all()

    app.run( debug=True)
