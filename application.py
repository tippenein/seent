from app.app import app
import os

ENV = os.getenv('ENV')

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5001))
  app.run(host='0.0.0.0', port=port, debug=ENV=='dev')
