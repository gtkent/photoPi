from webApp import create_app
import os

os.environ["SESSION_SECRET"]="MySessionSecret" 

app = create_app()
app.run(debug=True)
