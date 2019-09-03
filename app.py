from flask import Flask, render_template, request, redirect
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.models import NumeralTickFormatter
import requests
import json
#import os

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.ticker = None
app.check1 = 0
app.check2 = 0
app.check3 = 0
app.check4 = 0
app.check5 = 0
app.check6 = 0
app.counter = 0
app.year = 0

@app.route('/index',methods=['GET','POST'])
def index():

   if request.method == 'GET':
      return render_template('start.html')

   else:
      app.ticker = request.form['symbol']
      app.year = request.form['year']
      app.check1 = request.form.get('check1') #Closing Price
      app.check2 = request.form.get('check2') #Adj. Close
      app.check3 = request.form.get('check3') #Opening Price
      app.check4 = request.form.get('check4') #Adj. Open
      app.check5 = request.form.get('check5') #Volume
      app.check6 = request.form.get('check6') #Adj. Volume
      app.month = request.form.get('month')   #month

      #if not isinstance(app.ticker, str):
      #   return "Please retry: ticker entry is not type 'str'"
      if not isinstance(int(app.year), int):
         return "Please retry: year entry is not type 'int'"
      if len(list(app.year)) != 4:
         return 'The chosen year entry is not reasonable. Please go back and try again.' 

      check1 = False
      check2 = False
      check3 = False
      check4 = False
      check5 = False
      check6 = False
      if app.check1:
         check1 = True
         #return '1 is checked'
      if app.check2:
         check2 = True
         #return '2 is checked'
      if app.check3:
         check3 = True
         #return '3 is checked'
      if app.check4:
         check4 = True
         #return '4 is checked'
      if app.check5:
         check5 = True
         #return '5 is checked'
      if app.check6:
         check6 = True
         #return '6 is checked'

      last_day_dict = {'1':'31','2':'28','3':'31','4':'30','5':'31','6':'30','7':'31','8':'31','9':'30','10':'31','11':'30','12':'31'}
      month_dict = {'1':'January', '2':'February', '3':'March', '4':'April', '5':'May', '6':'June', '7':'July', '8':'August', '9':'September', '10':'October', '11':'November', '12':'December'}

      url = 'https://www.quandl.com/api/v3/datasets/WIKI/'+ app.ticker +'/data.json?api_key=ga7tsANscDBzn5CqMsgt'
      if app.month != '13':
         start_date = str(app.year) + '-' + app.month + '-1'
         end_date = str(app.year) + '-' + app.month + '-' + last_day_dict[app.month]
         payload = {'start_date': start_date, 'end_date': end_date}
         resp = requests.get(url, payload)
      else:
          resp = requests.get(url)
      if resp.status_code != 200:
         return 'Request for data using stock symbol "' + app.ticker + '" failed. Please go back and try again.'
      d1 = resp.json()
      df = pd.DataFrame(d1['dataset_data']['data'], columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Ex-Dividend', 'Split Ratio', 'Adj. Open', 'Adj. High', 'Adj. Low', 'Adj. Close', 'Adj. Volume'])
      df.Date  = pd.to_datetime(df.Date)
      if df.empty:
         return 'The requested data does not exist in the Quandl API'

      if app.month != '13':
         title_string = app.ticker + ' Stock Movement for ' + month_dict[app.month] + ' ' + str(app.year)
      else:
         title_string = app.ticker + ' Stock Movement'
      plot = figure(title=title_string, x_axis_label='Date', x_axis_type='datetime')
      plot.yaxis[0].formatter = NumeralTickFormatter(format="$0,0.00")
      if check1:
         plot.line(df.Date, df.Close, legend='Closing Price', line_color='black')
         #plot.square(df.Date, df.Close, legend='Closing Price', fill_color="black", line_color="black", size=8)
      if check2:
         plot.line(df.Date, df['Adj. Close'], legend='Adjusted Closing Price', line_color='red', line_dash='dashed')
         #plot.circle(df.Date, df['Adj. Close'], legend='Adjusted Closing Price', fill_color="red", line_color="red", size=4)
      if check3:
         plot.line(df.Date, df.Open, legend='Opening Price', line_color='blue')
         #plot.square(df.Date, df.Open, legend='Opening Price', fill_color="blue", line_color="blue", size=8)
      if check4:
         plot.line(df.Date, df['Adj. Open'], legend='Adjusted Opening Price', line_color='yellow', line_dash='dashed')
         #plot.circle(df.Date, df['Adj. Open'], legend='Adjusted Opening Price', fill_color="yellow", line_color="yellow", size=4)
      if check5:
         plot.line(df.Date, df.Volume, legend='Volume', line_color='orange')
         #plot.square(df.Date, df.Volume, legend='Volume', fill_color="orange", line_color="orange", size=8)
         plot.yaxis[0].formatter = NumeralTickFormatter(format="0.00 a")
      if check6:
         plot.line(df.Date, df['Adj. Volume'], legend='Adjusted Volume', line_color='purple', line_dash='dashed')
         #plot.circle(df.Date, df['Adj. Volume'], legend='Adjusted Volume', fill_color="purple", line_color="purple", size=4)
         plot.yaxis[0].formatter = NumeralTickFormatter(format="0.00 a")

      plot.legend.location = 'top_left'
      plot.xaxis[0].ticker.desired_num_ticks = 10
      html = file_html(plot, CDN, "my plot",_always_new=True)

      #file_script = 'templates/lines' + str(app.counter) + '.html'
      #with open(file_script,'w') as f:
      with open('templates/lines.html','w') as f:
         f.write(html)

      #with open('note.txt', 'w') as f:
      #   f.write('ticker is ' + app.ticker + '\n')
      #   f.write('check 1 is ' + str(check1) + '\n')
      #   f.write('check 2 is ' + str(check2) + '\n')
      #   f.write('check 3 is ' + str(check3) + '\n')

      #return render_template('lines' + str(app.counter) + '.html')
      return render_template('lines.html')
      #return render_template('l.html')

if __name__ == '__main__':
  app.run(port=33507)
  #port = int(os.environ.get("PORT", 5000))
  #app.run(host='0.0.0.0', port=port)
