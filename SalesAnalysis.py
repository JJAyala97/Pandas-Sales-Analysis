#!/usr/bin/env python
# coding: utf-8

# <h1>Solving Real Life Problems</h1>

# <h3>Import necessary libraries</h3>

# In[23]:


import pandas as pd 
import os
import datetime
import calendar
import matplotlib.pyplot as plt
import matplotlib.ticker as tick


# <i>Merging 12 months of sales data into a single file</i>

# In[24]:


df = pd.read_csv("./Sales_Data/Sales_April_2019.csv")


# In[25]:


df.head()


# In[26]:


files = [file for file in os.listdir('./Sales_Data')]
for file in files:
    print(file)


# In[27]:


all_months = pd.DataFrame()


# In[28]:


for file in files:
    df = pd.read_csv('./Sales_Data/'+file)
    all_months = pd.concat([all_months, df])
    


# In[29]:


all_months.head()


# In[30]:


all_months.to_csv("All_data.csv", index=False)


# In[34]:


all_data = pd.read_csv("All_data.csv", parse_dates = True)
all_data.head()


# ## Best Month for Sales?

# In[39]:


all_data['Month'] = all_data['Order Date'].str[0:2]
all_data['Month'] = all_data['Month'].astype('int32')
all_data.head()


# ### Dropping NaNs (Cleaning my data)

# In[35]:


nan_df = all_data[all_data.isna().any(axis=1)]
nan_df


# In[36]:


all_data = all_data.dropna(how="all")
all_data.head(1797)


# In[37]:


temp_df = all_data[all_data['Order Date'].str[0:2] == 'Or']
temp_df.head()


# In[38]:


all_data = all_data[all_data['Order Date'].str[0:2] != 'Or']


# #### A way to convert the month number to the month name

# In[40]:


all_data['Month'] = all_data['Month'].apply(lambda x: calendar.month_name[x])


# In[41]:


all_data.loc[:, 'Quantity Ordered'] = pd.to_numeric(all_data['Quantity Ordered'])
all_data.loc[:, 'Price Each'] = pd.to_numeric(all_data['Price Each'])

all_data.loc[:,'Sales'] = all_data['Quantity Ordered'] * all_data['Price Each']


# ## Creating Sales Column

# In[42]:


all_data


# In[43]:


all_data.sort_values(by=['Sales'], ascending=False)


# # Answer for Best Month for Sales

# In[44]:


results = all_data.groupby('Month').sum()


# #### Reformatting the Y axis tickers so that millions are more easily understood and visualized 

# In[45]:


def reformat_large_tick_values(tick_val, pos):
    """
    Turns large tick values (in the billions, millions and thousands) such as 4500 into 4.5K and also appropriately turns 4000 into 4K (no zero after the decimal).
    """
    if tick_val >= 1000000000:
        val = round(tick_val/1000000000, 1)
        new_tick_format = '{:}B'.format(val)
    elif tick_val >= 1000000:
        val = round(tick_val/1000000, 1)
        new_tick_format = '{:}M'.format(val)
    elif tick_val >= 1000:
        val = round(tick_val/1000, 1)
        new_tick_format = '{:}K'.format(val)
    elif tick_val < 1000:
        new_tick_format = round(tick_val, 1)
    else:
        new_tick_format = tick_val

    # make new_tick_format into a string value
    new_tick_format = str(new_tick_format)
    
    # code below will keep 4.5M as is but change values such as 4.0M to 4M since that zero after the decimal isn't needed
    index_of_decimal = new_tick_format.find(".")
    
    if index_of_decimal != -1:
        value_after_decimal = new_tick_format[index_of_decimal+1]
        if value_after_decimal == "0":
            # remove the 0 after the decimal point since it's not needed
            new_tick_format = new_tick_format[0:index_of_decimal] + new_tick_format[index_of_decimal+2:]
            
    return new_tick_format


# In[46]:


months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
plt.figure(figsize=(16,7))
plt.bar(months, results['Sales'])
plt.xticks(months)
plt.ylabel('Sales in USD ($)')
plt.xlabel('Month number')
ax = plt.gca()
ax.yaxis.set_major_formatter(tick.FuncFormatter(reformat_large_tick_values));
plt.show()


# In[47]:


all_data.to_csv("updated_data.csv", index=False)


# #### What city had the highest number of sales?

# In[48]:


all_data


# In[49]:


def get_city(address):
    return address.split(",")[1]

def get_state(address):
    return address.split(",")[2].split(' ')[1]
    
all_data['City'] = all_data["Purchase Address"].apply(lambda x: get_city(x) + ' ' + "(" + get_state(x) + ")")
all_data 


# In[50]:


salespercity = all_data.groupby('City').sum()


# In[51]:


cities = [city for city, df in all_data.groupby('City')]
plt.figure(figsize=(16,7))
plt.bar(cities, salespercity['Sales'])
plt.xticks(cities, rotation='vertical')
plt.ylabel('Sales in USD ($)')
plt.xlabel('Cities')
ax = plt.gca()
ax.yaxis.set_major_formatter(tick.FuncFormatter(reformat_large_tick_values));
plt.show()


# ## What time should we display adverisements to maximize likelihood of customer's buying products? 

# In[52]:


all_data['Order Date'] = pd.to_datetime(all_data['Order Date'])
all_data.head()


# In[53]:


all_data['Hour'] = all_data['Order Date'].dt.hour
all_data.head()


# In[54]:


hours = [hour for hour, df in all_data.groupby('Hour')]
plt.plot(hours, all_data.groupby(['Hour']).count())
plt.xticks(hours)
plt.grid()
plt.show()


# ### What products are most commonly sold together?

# In[56]:


all_data.head()


# In[57]:


df = all_data[all_data['Order ID'].duplicated(keep=False)]
df['Grouped'] = df.groupby('Order ID')['Product'].transform(lambda x: ', '.join(x))
df = df[['Order ID', 'Grouped']].drop_duplicates()
df.head()


# In[58]:


from itertools import combinations
from collections import Counter

count = Counter()

for row in df['Grouped']:
    row_list = row.split(',')
    count.update(Counter(combinations(row_list, 2)))
    
    
count.most_common(10)


# #### What product sold the most and why do you think?

# In[60]:


all_data.head()


# In[61]:


productgroup = all_data.groupby('Product')
quantity_ordered = productgroup.sum()['Quantity Ordered']

productgroup.sum()


# In[62]:


products = [product for product, df in productgroup]
plt.figure(figsize=(16,7))
plt.bar(products, quantity_ordered)
plt.xticks(products, rotation='vertical', size=12)
plt.ylabel('Quantity Ordered')
plt.xlabel('Products')
ax = plt.gca()
ax.yaxis.set_major_formatter(tick.FuncFormatter(reformat_large_tick_values));
plt.show()


# In[63]:


prices = all_data.groupby('Product').mean()['Price Each']
prices


# In[64]:




fig, ax1 = plt.subplots(figsize=(16,7))

ax2 = ax1.twinx()
plt.figure(figsize=(16,7))
ax1.bar(products, quantity_ordered, color='g')
ax2.plot(products, prices, 'b-')

ax1.set_xlabel('Product')
ax1.set_ylabel('Quantity Ordered', color='g')
ax2.set_ylabel('Price ($)', color='b')
ax1.set_xticklabels(products, rotation='vertical', size=8)



plt.show()


# In[ ]:




