# unimelb-results-autochecker

Sample use:

```
python main.py -u abc -p abc010101 -c "Bachelor of Science" -g abc@example.com -P abc010101 -f 1200
```

This will check your result for your Bachelor of Science degree (which is the short title shown on 'Choose a Study Plan' page)  every 20 minutes.

If there is a change in your WAM, it will send notification email to your gmail account (using your gmail server).

You will also see console outputs like this:
```
------------------------------------------
(Logging in...)
(Getting your result...)
Your Weight. Average is xx.xxx. This was calculated on xx-xx-xxxx.
(As at 10:34AM on November 21, 2018)
(No WAM change detected)
------------------------------------------
(Logging in...)
(Getting your result...)
Your Weight. Average is xx.xxx. This was calculated on xx-xx-xxxx.
(As at 11:05AM on November 21, 2018)
(No WAM change detected)
------------------------------------------
```
