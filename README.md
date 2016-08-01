# Train Ticket Informing
  A little python project can inform you when the train you want to take has ticket(s) left by email.

## Screenshot AND Usage

Filled in:  
```
# here is your user name
fr_user = ' '
# here is your password
fr_pwd = ' '
# here is your target
to_e_address = ' '
# here is your target's smtp server ( Tencent: smtp.qq.com )
SMTP_server = 'smtp.qq.com'
# here is your target's smtp server port ( Tencent: 465 )
SMTP_port = 465
```

Run it.  
You can see:  
Init  
![image](https://raw.githubusercontent.com/TimHsue/TrainTicketQuery/master/screenshot/1.png)  

Then if you want to subscribe a new train, type in 'new', you will see:  
New  
![image](https://raw.githubusercontent.com/TimHsue/TrainTicketQuery/master/screenshot/2.png)  

Here is all the subscriptions:  
Status  
![image](https://raw.githubusercontent.com/TimHsue/TrainTicketQuery/master/screenshot/3.png)  

If you want to unsubscribe a train, you can type in 'kill', then you will see:  
Del  
![image](https://raw.githubusercontent.com/TimHsue/TrainTicketQuery/master/screenshot/4.png)

After xxdone you will see in your target email:  
Response  
![image](https://raw.githubusercontent.com/TimHsue/TrainTicketQuery/master/screenshot/5.png)  


# Attention!
Python should support the https service  
DONT DEL 'IN'
