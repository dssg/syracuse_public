#!/bin/bash
./CleanWaterWorkOrders.py
psql -f createtable.script
