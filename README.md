# Parameter Plugin
This is a Fusion 360 API ADD-IN that evaluates logical operators and conditional expressions added to the comment of a Design Parameter this can be used to preform Ilogic like operations in Fusion 360 

![image](https://user-images.githubusercontent.com/41913546/133493654-20025c53-a8b9-45b6-b600-4118d8062314.png)

# Installation
Clone or download the Parameter Plugin folder

Unzip the Folder 

In the Fusion 360 Model enviorment click tools

![image](https://user-images.githubusercontent.com/41913546/133494188-0aa6126f-346d-40a4-a765-dd72bd56156a.png)

Click ADD-INS

![image](https://user-images.githubusercontent.com/41913546/133494685-ba837eda-a8ed-4d1b-8334-fc2cc7824131.png)

Click the second Tab ADD-INS

![image](https://user-images.githubusercontent.com/41913546/133494781-59c0c5df-53ea-4dd9-a39b-72e7f251caf6.png)

Click the green plus To add the ADD-IN

![image](https://user-images.githubusercontent.com/41913546/133494941-3e17728d-91d8-410d-b3a9-934afcc85fea.png)

Select the Downloaded folder 

![image](https://user-images.githubusercontent.com/41913546/133495151-14018ef2-3f27-41cd-84b7-975f9a96f2fa.png)

Click Select folder 

![image](https://user-images.githubusercontent.com/41913546/133495179-43174e1d-4a38-4d91-98ad-7c71251d9ce5.png)

Wait for the folder to load

![image](https://user-images.githubusercontent.com/41913546/133495724-ebab3595-6ec4-4b7f-9031-22dbdc65e66e.png)

Click Run

![image](https://user-images.githubusercontent.com/41913546/133495808-001a2f96-d444-4df0-a42f-19d005659615.png)

If the Add-In started this message will be displayed

![image](https://user-images.githubusercontent.com/41913546/134031217-bfce65d4-1890-42ce-aa6e-34dfeeec3f40.png)

Go Back to the Solid Tab, the ADD-IN will be added to the Modify panel

![image](https://user-images.githubusercontent.com/41913546/133495933-52007e0b-a520-4254-aa2a-c0adc6f9335f.png)

Click the Plugin

![image](https://user-images.githubusercontent.com/41913546/133496331-fdca7b0d-05b5-4907-87a2-7d6c4c1a7ea1.png)

Note:
The Plugin will only start if a model has assigned user parameters 

# Usage
1. Enter the Model Enviorment
2. Add User Parameters to the model
3. Select Modify -> Change Parameters

![image](https://user-images.githubusercontent.com/41913546/133497057-5d4b3650-673b-4017-a754-2187b5d12c5e.png)

4. Add Model parameters 
5. In the Parameters Comment add a logical expression: ex. if OD_IN >7:; OD_IN = OD_IN;else:;  OD_IN=11; 

The line will be evaluated as

![image](https://user-images.githubusercontent.com/41913546/133498258-fa06e725-5ef5-4272-bcb8-45eda5b18d6c.png)

Notes:

Semicolons are used to end lines and are replaced with a new line character,

All expressions are evaluated using python 3 syntax so spacing needs to be consistent 

6. Run The Parameter Plugin

![image](https://user-images.githubusercontent.com/41913546/133498563-42ab1d97-7e12-45e9-aa4f-fea5d765d7a0.png)

7. The Plugin will open up 

![image](https://user-images.githubusercontent.com/41913546/133498621-4f2f1df0-93bb-46e3-949a-5f9cc4a5c440.png)

8. Click okay and the model will be updated

![image](https://user-images.githubusercontent.com/41913546/133499313-6fbfc388-0607-4c60-83f6-05ad5f4e3810.png)

9. Syntax issues will be displayed in warnings

![image](https://user-images.githubusercontent.com/41913546/133498447-3eeae4fe-16a6-4818-a53a-55473c811c4d.png)



