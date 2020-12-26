from time import sleep
import json
from datetime import datetime
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options as Chrome_options
from Building import Building
from Utils import wait,wait_until,click,pressEscape,dated_message,string_to_delta_time,date_to_string,click_ac
import Events
import Files
import Game



'''
Admin: Allow the bot to upgrade buildings esily using buildings window + Bot can use culture window.
Captain: Allow the bot to use the window of villages to loot them easily.
'''

class Game:
	cities = []
	def __init__(self,browser,files,queue,flag,update_function,finish_function):
		self.browser = browser
		self.files = files
		self.queue = queue
		self.flag = flag
		self.update_function = update_function
		self.finish_function = finish_function
	# Files
	def load_settings(self):
		self.settings = self.files.get_settings()
		server = self.settings['player']['server']
		server = server.replace("https://","").replace(".grepolis.com/","")
		#print(server)
		self.translation = self.settings['Translation'][server.upper()]

	# Cities
	def open_cities_list(self):
	    ac = ActionChains(self.browser)
	    listButton = self.browser.find_element_by_xpath("//div[@class='town_name_area']//div[@class='caption js-viewport']")
	    ac.move_to_element(listButton).move_by_offset(0, 0).click().perform()
	    sleep(2)	

	def get_cities(self):
		self.open_cities_list()

		citiesList = self.browser.find_elements_by_xpath("//div[contains(@class,'town_groups_list')]//div[@data-groupid ='-1']//div[contains(@class,'item')][@data-townid]")

	    #print("Number of cities: ", len(citiesList))

		for city in citiesList:
		    id = city.get_attribute('name')
		    name = city.find_element_by_xpath("./span[@class='town_name']").text
		    self.settings['cities'][name] = {}
		    self.settings['cities'][name]['id'] = id
		    self.settings['reverse_map'][id] = name
	        #print(id,"<---->",name)

		citiesGroups = self.browser.find_elements_by_xpath("//div[contains(@class,'group_name')]//div[@class='name']")
		citiesGroupsNames = [x.text.split(" ")[0] for x in citiesGroups]
		citiesGroupsIds = [x.get_attribute("data-groupid") for x in citiesGroups]

		for i in range(len(citiesGroups)):
		    if(citiesGroupsNames[i] in self.settings['groups']):
		        self.settings['groups'][citiesGroupsNames[i]]['id'] = citiesGroupsIds[i]
		        citiesList = self.browser.find_elements_by_xpath("//div[contains(@class,'town_groups_list')]//div[@data-groupid ='"+ citiesGroupsIds[i] +"']//div[contains(@class,'item')][@data-townid]")
		        for city in citiesList:
		            name = city.find_element_by_xpath("./span[@class='town_name']").text
		            self.settings['cities'][name]['group'] = citiesGroupsNames[i]

		#print(settings['cities'])

		#print(citiesGroupsNames)
		#print(citiesGroupsIds)

		self.open_cities_list()

		self.cities = list(self.settings['cities'].keys())
		self.cities.reverse()


	def go_to_city(self,city = None):
	    if (city == None):
	        return
	    if(city != self.browser.find_element_by_class_name('town_name').text):
	        self.open_cities_list()
	        sleep(2)
	        ac = ActionChains(self.browser)
	        xpath = "//div[@data-townid = " + "'" + self.settings['cities'][city]['id'] + "']"
	        cityButton = self.browser.find_element_by_xpath(xpath)
	        self.browser.execute_script("$(arguments[0]).click();", cityButton)
	        #ac.move_to_element(cityButton).move_by_offset(0, 0).click().perform()
	        sleep(2)

	# Actions Scheduler
	def add_action(self,time,action,city):
		self.queue.add_action(time,action,city)

	def do_next_action(self):
		res = 2
		if not self.queue.empty() and not self.flag.get():
			date,action,city = self.queue.get_action()
			wait_until(date)
			if self.flag.get() :
				self.add_action(date,action,city)
				return

			# Schedule next time the actions must be done:
			deltaTime = timedelta(minutes=int(self.settings['times'][action.__name__]))
			newTime = datetime.now()+deltaTime
			dated_message('Setting ' + action.__name__ + ' for ' + date_to_string(newTime))
			self.add_action(newTime,action,city)

			# Try to do the action:
			try :
				dated_message('Starting: ' + action.__name__ + '')
				self.go_to_city(city)
				res = action(city)
				dated_message('Finishing: ' + action.__name__ + '')
			except Exception as e:
				dated_message('Error in '+ action.__name__ + ': \n' + str(e))
				self.browser.save_screenshot('Error.png')
		return res
	
	# Different actions

	def village_loot(self,city):
   		#go to island view
	    goToIslandViewButton = self.browser.find_element_by_class_name('island_view')
	    click(goToIslandViewButton)
	    showCurrentIslandButton = self.browser.find_element_by_class_name('btn_jump_to_town')
	    ac = ActionChains(self.browser)
	    ac.move_to_element(showCurrentIslandButton).move_by_offset(0, 0).click().perform()
	    sleep(2)
	    pressEscape(self.browser)

	    # reap all villages that are available
	    while len(self.browser.find_elements_by_class_name('claim')) > 0:
	        pressEscape(self.browser)
	        # open village window
	        villageLink = self.browser.find_element_by_class_name('claim')
	        actions = ActionChains(self.browser)
	        actions.move_to_element(villageLink).click().perform()
	        sleep(1)

	        # make sure we're allowed to collect resources
	        if len(self.browser.find_element_by_class_name('pb_bpv_unlock_time').text) == 0:
	            # click on button to collect resources
	            try:
	                upgradeVillageButton = self.browser.find_element_by_class_name('btn_upgrade')
	                cost = int(upgradeVillageButton.text.split(" ")[1])
	                if(self.settings['player']['upgrade_villages'] and cost <= self.settings['player']['village_battle_points']):
	                    click(upgradeVillageButton)
	            except Exception:
	                pass
	            collectResourcesButtons = self.browser.find_elements_by_class_name('card_click_area')
	            click(collectResourcesButtons[0])
	            pressEscape(self.browser)

	        # close village window
	        pressEscape(self.browser)

	def upgrade_villages(self,city):
   		#go to island view
	    goToIslandViewButton = self.browser.find_element_by_class_name('island_view')
	    click(goToIslandViewButton)
	    showCurrentIslandButton = self.browser.find_element_by_class_name('btn_jump_to_town')
	    ac = ActionChains(self.browser)
	    ac.move_to_element(showCurrentIslandButton).move_by_offset(0, 0).click().perform()
	    sleep(2)
	    pressEscape(self.browser)

	    # reap all villages that are available
	    for village in self.browser.find_elements_by_class_name('claim'):
	        pressEscape(self.browser)
	        # open village window
	        villageLink = village
	        actions = ActionChains(self.browser)
	        actions.move_to_element(villageLink).click().perform()
	        sleep(1)

	        # make sure we're allowed to collect resources
	        if len(self.browser.find_element_by_class_name('pb_bpv_unlock_time').text) == 0:
	            # click on button to collect resources
	            try:
	                upgradeVillageButton = self.browser.find_element_by_class_name('btn_upgrade')
	                cost = int(upgradeVillageButton.text.split(" ")[1])
	                if(self.settings['player']['upgrade_villages'] and cost <= self.settings['player']['village_battle_points']):
	                    click(upgradeVillageButton)
	            except Exception:
	                pass
	            pressEscape(self.browser)

	        # close village window
	        pressEscape(self.browser)

	def village_loot_captain(self,city):
		self.go_to_premium_villages()
		sleep(2)
		try:
			select_all_button = self.browser.find_element_by_xpath("//a[contains(@class,'select_all')]")
			click(select_all_button)
			sleep(3)
			click(self.browser.find_element_by_id("fto_claim_button"))
			sleep(2)
			
			try:
				yes_button = self.browser.find_element_by_xpath("//div[@class = 'confirmation']//div[@class='buttons']//div[contains(@class,'caption')]")
				click(yes_button)
			except Exception as e:
				print(e)

		except Exception as e:
			print(e)	

		self.clean_open_windows()



	def village_loot_captain_old(self,city):
	    self.go_to_premium_villages()
	    sleep(2)

	    for city in self.settings['cities'].keys():
	        try :
	            name = "town" + self.settings['cities'][city]['id']
	            villageButton = self.browser.find_element_by_xpath("//li[contains(@class,'"+name+"')]")
	            self.browser.execute_script("$(arguments[0]).click();", villageButton)
	            sleep(3)
	            click(self.browser.find_element_by_id("fto_claim_button"))
	        except Exception as e:
	            print(e)
	    self.clean_open_windows()


	def go_to_city_overview(self):
	    click(self.browser.find_element_by_class_name('city_overview'))

	def go_to_premium(self):
	    premiumButton = self.browser.find_element_by_class_name("premium")
	    click(premiumButton)

	def go_to_premium_buildings(self):
	    self.go_to_premium()
	    buldingsButton = self.browser.find_element_by_id("town_overviews-building_overview")
	    click(buldingsButton)

	def go_to_premium_villages(self):
	    premiumMenu = self.browser.find_element_by_class_name('premium')
	    ac = ActionChains(self.browser)
	    ac.move_to_element(premiumMenu).move_by_offset(0, 0)
	    villages = self.browser.find_element_by_xpath("//li[@class='farm_town_overview']//a[@name='farm_town_overview']")
	    ac.move_to_element(villages).move_by_offset(0, 0).click().perform()


	def open_senate(self):
	    self.browser.execute_script("""BuildingWindowFactory.open('main');""")
	    sleep(2)

	def open_market(self):
	    self.browser.execute_script("""BuildingWindowFactory.open('market');""")
	    sleep(2)

	def open_academy(self):
	    self.browser.execute_script("""BuildingWindowFactory.open('academy');""")
	    sleep(2)

	def open_barracks(self):
	    self.browser.execute_script("""BuildingWindowFactory.open('barracks');""")
	    sleep(2)

	def open_harbor(self):
	    self.browser.execute_script("""BuildingWindowFactory.open('harbor');""")
	    sleep(2)

	def clean_open_windows(self):
	    sleep(1)
	    pressEscape(self.browser)
	    sleep(0.4)
	    pressEscape(self.browser)
	    sleep(1)

	def building_premium(self,city):
	    premiumButton = self.browser.find_element_by_xpath("//div[@class='toolbar_button premium']")
	    click(premiumButton)
	    sleep(4)
	    cultureButton = self.browser.find_elements_by_xpath("//li/a[@data-menu_name='Edificio']")
	    click_ac(self.browser,cultureButton[0])
	    sleep(4)


	def culture(self,city):
	    premiumButton = self.browser.find_element_by_xpath("//div[@class='toolbar_button premium']")
	    click(premiumButton)
	    sleep(4)
	    cultureButton = self.browser.find_elements_by_xpath("//li/a[@data-menu_name='Cultura']")
	    click_ac(self.browser,cultureButton[0])
	    sleep(4)
	    confirmButton = self.browser.find_elements_by_xpath("//a[@id='start_all_celebrations'][@class='confirm']")
	    #print(len(confirmButton))
	    click_ac(self.browser,confirmButton[0])


	def academy(self,city):
	    academySettings = self.settings['academy']
	    self.open_academy()
	    investigateButtons = self.browser.find_elements_by_class_name('btn_upgrade')
	    for item in investigateButtons:
	        if(item.get_attribute('data-research_id') in academySettings and academySettings[item.get_attribute('data-research_id')]):
	            click(item)
	            investigateButtons = self.browser.find_elements_by_class_name('btn_upgrade')

	    self.clean_open_windows()


	def academy_groups(self,city):
	    academySettings = self.settings['groups'][self.settings['cities'][city]['group']]['academy']
	    self.open_academy()
	    investigateButtons = self.browser.find_elements_by_class_name('btn_upgrade')
	    for item in investigateButtons:
	        if(item.get_attribute('data-research_id') in academySettings and academySettings[item.get_attribute('data-research_id')]):
	            click(item)
	            investigateButtons = self.browser.find_elements_by_class_name('btn_upgrade')

	    self.clean_open_windows()


	def time_reduction(self):
	    try:
	        timeReductionButtons = self.browser.find_elements_by_class_name('btn_time_reduction')

	        if(len(timeReductionButtons) > 0):
	            if(timeReductionButtons[0].text == "Gratis"):
	                click(timeReductionButtons[0])
	    except Exception as e:
	        dated_message('Error in timeReduction: \n' + str(e))


	def upgrade_buildings(self,city):
	    buildingSettings = self.settings['buildings']
	    self.open_senate()
	    self.time_reduction()
	    sleep(2)
	    buildings = self.building_array(buildingSettings)
	    timeToLive = 0
	    while (len(buildings) > 0) and timeToLive < 8:
	        # upgradge building whose furthest from goal
	        buildingToUpgrade = max(buildings, key = lambda x: x.percentToGoal())
	        click(buildingToUpgrade.htmlButton)
	        self.time_reduction()
	        sleep(2)
	        buildings = self.building_array(buildingSettings)
	        timeToLive += 1
	    sleep(2)

	    self.clean_open_windows()



	def building_array(self,buildingSettings):

	    allButtons = self.browser.find_elements_by_class_name('build_up')
	    buildings = []
	    k = 0
	    while k < len(buildingSettings):
	        newBuilding = Building(buildingSettings[k], allButtons[k])
	        if newBuilding.haveEnoughResources and newBuilding.priority > 0:
	            buildings.append(newBuilding)
	        k += 1

	    return buildings


	def end(self,city = None):
		self.update_function('Finished playing.')
		print("End.")
		self.browser.quit()
		self.finish_function()
		return 1