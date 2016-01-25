NAME = 'HBrowse'
URL_BASE = "http://www.hbrowse.com"
URL_BROWSE_BASE = URL_BASE + "/browse"
URL_BROWSE_CAT = URL_BROWSE_BASE + "/{0}"
URL_BROWSE_CAT_SUB = URL_BROWSE_BASE + "/{0}/{1}"
# the thumbs used in listing the books
URL_BOOK_THUMB_1 = URL_BASE + "/thumbnails/{0}_1.jpg"
URL_BOOK_THUMB_2 = URL_BASE + "/thumbnails/{0}_2.jpg"

THUMBS_PAGE = "http://www.hbrowse.com/thumbnails/{0}/{1}"
THUMBS_IMG_XPATH = "//div[@id='main']/table/tr/td/a/img[@style='width:120px;height:auto;border:1px solid #000;']"

ICON = "icon-default.png"

ORDER_BY_URLS = {
    "title_asc":   "/title/ASC",
    "title_desc":  "/title/DESC",
    "date_desc":   "/date/DESC",
    "date_asc":    "/date/ASC",
    "length_desc": "/length/DESC",
    "length_asc":  "/length/ASC",
    "rank_desc":   "/length/DESC",
    "rank_asc":    "/length/ASC",
    "random":      "/random",
}

ORDER_BY_NAMES = [
    "title_asc",
    "title_desc",
    "date_desc",
    "date_asc",
    "length_desc",
    "length_asc",
    "rank_desc",
    "rank_asc",
    "random"
]

CATEGORIES = [
    'genre', 'type', 'setting', 'fetish',
    'role', 'relationship', 'maleBody', 'femaleBody',
    'grouping', 'scene', 'position'
]

ALPHABET = list('abcdefghijklmnopqrstuvwxyz')
ALPHABETICAL_CATEGORIES = ['title', 'artist', 'origin']

####################################################################################################
def Start():

    ObjectContainer.title1 = NAME
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
    Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("Images", viewMode="Pictures", mediaType="items")

    if 'adv_search_history' not in Dict:
        Dict['adv_search_history'] = []
    if 'search_history' not in Dict:
        Dict['search_history'] = []

    Dict.Save()

@handler('/photos/hbrowse', NAME, ICON)
def MainMenu():

    oc = ObjectContainer()

    oc.add(DirectoryObject(key=Callback(ListCategories),
                           title=u'%s: %s' % (L('browse'), L('categories'))))

    oc.add(DirectoryObject(key=Callback(ListBooks,
                                        category='title',
                                        sort_method='date_desc'),
                           title=u'%s: %s' % (L('browse'), L('latest'))))

    oc.add(DirectoryObject(key=Callback(ListBooks,
                                        category='title',
                                        sort_method='rank_desc'),
                           title=u'%s: %s' % (L('browse'), L('highest_rank'))))

    for item in ALPHABETICAL_CATEGORIES:
        oc.add(DirectoryObject(key=Callback(ListAlphabetical,
                                            category=item),
                               title=u'%s: %s' % (L('browse'), L(item))))

    oc.add(InputDirectoryObject(key=Callback(Search),
                                title=L('text_search')))

    oc.add(DirectoryObject(key=Callback(SearchAdvancedIncludes),
                           title=L('advanced_search')))

    oc.add(DirectoryObject(key=Callback(SearchHistory),
                           title=L('search_history')))

    oc.add(DirectoryObject(key=Callback(SearchAdvancedHistory),
                           title=L('advanced_search_history')))

    oc.add(PrefsObject(title=L('preferences')))

    return oc

####################################################################################################
# Search
####################################################################################################
@route('/photos/hbrowse/search')
def Search(query):

    if not query:
        return ObjectContainer()

    if len(query) <= 3:
        return ObjectContainer()

    query = query.strip()

    url = "http://www.hbrowse.com/content/process.php"

    post = {
        "type":  "search",
        "needle": query.strip()
    }

    search_history = Dict['search_history']
    if not query in search_history:
        search_history.append(query)
        Dict['search_history'] = search_history
        Dict.Save()

    data = HTTP.Request(url=url, values=post)

    return ListBooks(page_data=data.content)

@route('/photos/hbrowse/search/history')
def SearchHistory():

    oc = ObjectContainer()

    search_history = Dict['search_history']

    for item in search_history:
        oc.add(DirectoryObject(key=Callback(Search, query=item),
                               title=u'%s' % item))

    return oc

@route('/photos/hbrowse/search/advanced')
def SearchAdvanced(includes, excludes):

    search_item = [includes.strip(), excludes.strip()]
    includes = includes.strip().split()
    excludes = excludes.strip().split()

    url = "http://www.hbrowse.com/content/process.php"

    post = {"type": "advance"}

    for item in ADVANCED_SEARCH_TAGS:
        if item in includes:
            post[item] = "y"
        elif item in excludes:
            post[item] = "n"
        else:
            post[item] = ""

    adv_search_history = Dict['adv_search_history']
    if search_item not in adv_search_history:
        adv_search_history.append(search_item)
        Dict['adv_search_history'] = adv_search_history
        Dict.Save()

    data = HTTP.Request(url=url, values=post)

    return ListBooks(page_data=data.content)

@route('/photos/hbrowse/search/advanced/include')
def SearchAdvancedIncludes(includes=""):

    oc = ObjectContainer(no_history=True)

    oc.add(DirectoryObject(key=Callback(SearchAdvancedExcludes,
                                        includes=includes),
                           title=u'> %s' % L('proceed_to_exclusions')))

    for item in ADVANCED_SEARCH_TAGS:
        if item not in includes.split():
            oc.add(DirectoryObject(key=Callback(SearchAdvancedIncludes,
                                                includes='%s %s' % (includes, item)),
                                   title=u'%s: %s' % (L('include'), item)))

    return oc

@route('/photos/hbrowse/search/advanced/exclude')
def SearchAdvancedExcludes(includes="", excludes=""):

    oc = ObjectContainer(no_history=True)

    oc.add(DirectoryObject(key=Callback(SearchAdvanced,
                                        includes=includes,
                                        excludes=excludes),
                           title=u'%s' % L('execute_search')))

    for item in ADVANCED_SEARCH_TAGS:
        if item not in includes.split() and item not in excludes.split():
            oc.add(DirectoryObject(key=Callback(SearchAdvancedExcludes,
                                                includes=includes,
                                                excludes=excludes + " " + item),
                                   title=u'%s: %s' % (L('exclude'), item)))

    return oc

@route('/photos/hbrowse/search/advanced/history')
def SearchAdvancedHistory():

    adv_search_history = Dict['adv_search_history']

    oc = ObjectContainer()

    for item in adv_search_history:
        oc.add(DirectoryObject(key=Callback(SearchAdvanced,
                                            includes=item[0],
                                            excludes=item[1]),
                               title=u'+%s / -%s' % (item[0], item[1])))

    return oc

####################################################################################################
# Listings
####################################################################################################
@route('/photos/hbrowse/list/sortmethods/{category}/{sub_category}')
def ListSortMethods(category, sub_category):

    oc = ObjectContainer(title2=L('sort_method'))

    for method in ORDER_BY_NAMES:
        oc.add(DirectoryObject(key=Callback(ListBooks,
                                            category=category,
                                            sub_category=sub_category,
                                            sort_method=method),
                               title=L(method)))

    return oc

@route('/photos/hbrowse/list/categories')
def ListCategories():

    oc = ObjectContainer(title2=L('categories'))

    for category in CATEGORIES:
        oc.add(DirectoryObject(key=Callback(ListSubCategories,
                                            category=category),
                               title=category))

    return oc

@route('/photos/hbrowse/list/alphabetical/{category}')
def ListAlphabetical(category):

    oc = ObjectContainer()

    if category == "origin" or category == "artist":
        # these categories have a sub menu
        for letter in ALPHABET:
            oc.add(DirectoryObject(key=Callback(ListAlphabeticalItems,
                                                category=category,
                                                letter=letter),
                                   title=letter))
    else:
        for letter in ALPHABET:
            oc.add(DirectoryObject(key=Callback(ListSortMethods,
                                                category=category,
                                                sub_category=letter),
                                   title=letter))

    return oc

@route('/photos/hbrowse/list/alphabetical/{category}/{letter}')
def ListAlphabeticalItems(category, letter):

    oc = ObjectContainer()

    url = URL_BROWSE_CAT.format(category) + "/" + letter
    page = HTML.ElementFromURL(url)

    elements = page.xpath("//div[@id='main']/table[@class='listTable']/tr/td/strong/a")

    for item in elements:
        subcategory = item.text
        oc.add(DirectoryObject(key=Callback(ListSortMethods,
                                            category=category,
                                            sub_category=subcategory),
                               title=item.text))

    return oc

@route('/photos/hbrowse/list/subcategories/{category}')
def ListSubCategories(category):

    if Prefs['logging']: Log("HBROWSE: ListSubCategories " + category)

    oc = ObjectContainer(title2=L('sub_categories'))

    url = URL_BROWSE_CAT.format(category)
    page = HTML.ElementFromURL(url)

    elements = page.xpath("//td[@class='listShort']/strong")

    for item in elements:
        children = item.getchildren()

        subcategory = children[0].text
        if Prefs['logging']: Log("HBROWSE: ListSubCategories     -" + subcategory)

        oc.add(DirectoryObject(key=Callback(ListSortMethods,
                                            category=category,
                                            sub_category=subcategory),
                               title=subcategory))

    return oc

@route('/photos/hbrowse/list/books', page=int)
def ListBooks(category=None, sub_category=None, sort_method=None, page=1, page_data=None):

    if not page_data:
        if sub_category:
            title2 = "{0}/{1} - {2}".format(category, sub_category, L(sort_method))
        else:
            title2 = "{0} - {1}".format(category, L(sort_method))

        url = URL_BROWSE_CAT.format(category) if not sub_category else \
              URL_BROWSE_CAT_SUB.format(category, sub_category.replace(" ", "_"))
        url += ORDER_BY_URLS[sort_method]
        if Prefs['logging']: Log("HBROWSE: ListBooks - url=" + url)

        data = HTML.ElementFromURL(CleanUrl(url) + "/{0}".format(page),
                                   cacheTime=CACHE_1HOUR)
        oc = ObjectContainer(title2=title2)
    else:
        data = HTML.ElementFromString(page_data)
        oc = ObjectContainer(title2=L('search'), replace_parent=True)

    titles = data.xpath("//div[@class='thumbDiv']")

    for item in titles:
        children = item.getchildren()
        try:
            book_url = children[0].get('href')
        except:
            continue
        book_id = GetBookId(book_url)
        thumb = URL_BOOK_THUMB_1.format(book_id)
        try:
            title = children[0].get('title').split('\'')[1]
        except:
            title = '...'
        if Prefs['logging']: Log("HBROWSE: ListBooks - bookurl=" + book_url)

        oc.add(DirectoryObject(key=Callback(ListChapters,
                                            url=book_url,
                                            title=title),
                               title=title,
                               thumb=Resource.ContentsOfURLWithFallback(thumb)))

    if len(oc) > 0 and not page_data:
        oc.add(NextPageObject(key=Callback(ListBooks,
                                           category=category,
                                           sub_category=sub_category,
                                           sort_method=sort_method,
                                           page=page+1),
                              title=L('more')))

    return oc

@route('/photos/hbrowse/list/chapters/{title}')
def ListChapters(url, title):

    if Prefs['logging']: Log("HBROWSE: ListChapters - " + url)

    oc = ObjectContainer(title2="{0} - {1}".format(title, L('chapters')))
    url = String.Unquote(url) #ios was quoting the url when passed between functions
    url = CleanUrl(url)
    url_split = url.split('/')
    url = '/'.join(url_split[:-1])

    if Prefs['logging']: Log("HBROWSE: ListChapters - " + url)
    page = HTML.ElementFromURL(url)

    items = page.xpath("//div[@id='main']/table[@class='listTable']/tr/td[@class='listLeft']")

    for item in items:
        chapter_url = url
        chapter_title = title

        text = item.text
        if Prefs['logging']: Log("HBROWSE: ListChapters     - " + text)

        if text == "Cover Pages":
            chapter_url += "/c00000"
            chapter_title += " - Cover Pages"
        elif text.startswith("Chapter "):
            chapter = "00000" + text[-3:]
            chapter_url += "/c" + chapter[-5:]
            chapter_title += " - Chapter " + chapter_url[-3:]
        elif text == "Final Pages":
            chapter_url += "/c99999"
            chapter_title += " - Final Pages"
        elif text.startswith("Extra "):
            chapter = "00000" + text[-3:]
            chapter_url += "/c1" + chapter[-4:]
            chapter_title += " - Extra " + chapter_url[-3:]
        else:
            continue

        oc.add(PhotoAlbumObject(key=Callback(GetPhotoAlbum, url=chapter_url),
                                rating_key=chapter_url,
                                title=chapter_title))

    return oc

@route('/photos/hbrowse/photoalbum')
def GetPhotoAlbum(url):

    oc = ObjectContainer()

    url = url[:-1] if url.endswith('/') else url

    chapter = GetChapter(url)
    itemid = GetId(url)

    url = THUMBS_PAGE.format(itemid, chapter)

    page = HTML.ElementFromURL(url)

    images = page.xpath(THUMBS_IMG_XPATH)

    for image in images:
        thumb = image.get('src')
        image = UrlFromThumbUrl(thumb)

        oc.add(PhotoObject(url=image,
                           title=image.split('/')[-1],
                           thumb=Resource.ContentsOfURLWithFallback(thumb)))

    return oc

def GetChapter(url):
    return url.split('/')[-1]

def GetId(url):
    return url.split('/')[-2]

# thumb urls are /chapter/zzz/img.jpg, full img is without zzz
def UrlFromThumbUrl(url):
    return url.replace('zzz/', '')

def CleanUrl(url):
    return url[:-1] if url.endswith('/') else url

def GetBookId(url):
    return CleanUrl(url).split("/")[-2]

####################################################################################################
# all the tags for advanced searching
ADVANCED_SEARCH_TAGS = [
    "genre_action", "genre_adventure", "genre_anime", "genre_bizarre", "genre_comedy",
    "genre_drama", "genre_fantasy", "genre_gore", "genre_historic", "genre_horror", "genre_medieval",
    "genre_modern", "genre_myth", "genre_psychological", "genre_romance", "genre_school_life",
    "genre_scifi", "genre_supernatural", "genre_video_game", "genre_visual_novel",

    "type_anthology", "type_bestiality", "type_dandere", "type_deredere", "type_fully_colored", "type_futanari",
    "type_gender_bender", "type_guro", "type_harem", "type_incest", "type_kuudere", "type_lolicon",
    "type_long_story", "type_netorare", "type_non-con", "type_partly_colored", "type_reverse_harem",
    "type_ryona", "type_short_story", "type_shotacon", "type_transgender", "type_tsundere", "type_uncensored",
    "type_vanilla", "type_yandere", "type_yaoi", "type_yuri",

    "setting_amusement_park", "setting_attic", "setting_automobile", "setting_balcony", "setting_basement", "setting_bath",
    "setting_beach", "setting_bedroom", "setting_cabin", "setting_castle", "setting_cave", "setting_church",
    "setting_classroom", "setting_deck", "setting_dining_room", "setting_doctors", "setting_dojo",
    "setting_doorway", "setting_dream", "setting_dressing_room", "setting_dungeon", "setting_elevator",
    "setting_festival", "setting_gym", "setting_haunted_building", "setting_hospital", "setting_hotel",
    "setting_hot_springs", "setting_kitchen", "setting_laboratory", "setting_library", "setting_living_room",
    "setting_locker_room", "setting_mansion", "setting_office", "setting_other", "setting_outdoor",
    "setting_outer_space", "setting_park", "setting_pool", "setting_prison", "setting_public",
    "setting_restaurant", "setting_restroom", "setting_roof", "setting_sauna", "setting_school",
    "setting_school_nurses_office", "setting_shower", "setting_shrine", "setting_storage_room",
    "setting_store", "setting_street", "setting_teachers_lounge", "setting_theater", "setting_tight_space",
    "setting_toilet", "setting_train", "setting_transit", "setting_virtual_reality", "setting_warehouse",
    "setting_wilderness",

    "fetish_androphobia", "fetish_apron", "fetish_assertive_girl", "fetish_bikini",
    "fetish_bloomers", "fetish_breast_expansion", "fetish_business_suit", "fetish_chinese_dress",
    "fetish_christmas", "fetish_collar", "fetish_corset", "fetish_cosplay_(female)", "fetish_cosplay_(male)",
    "fetish_crossdressing_(female)", "fetish_crossdressing_(male)", "fetish_eye_patch", "fetish_food",
    "fetish_giantess", "fetish_glasses", "fetish_gothic_lolita", "fetish_gynophobia", "fetish_high_heels",
    "fetish_hot_pants", "fetish_impregnation", "fetish_kemonomimi", "fetish_kimono", "fetish_knee_high_socks",
    "fetish_lab_coat", "fetish_latex", "fetish_leotard", "fetish_lingerie", "fetish_maid_outfit",
    "fetish_none", "fetish_nonhuman_girl", "fetish_olfactophilia", "fetish_pregnant", "fetish_rich_girl",
    "fetish_school_swimsuit", "fetish_shy_girl", "fetish_sleeping_girl", "fetish_sporty", "fetish_stockings",
    "fetish_strapon", "fetish_student_uniform", "fetish_swimsuit", "fetish_tanned", "fetish_time_stop",
    "fetish_twins_(coed)", "fetish_twins_(female)", "fetish_twins_(male)", "fetish_uniform",
    "fetish_wedding_dress",

    "role_alien", "role_android", "role_athlete", "role_bride", "role_bunnygirl",
    "role_cheerleader", "role_delinquent", "role_demon", "role_doctor", "role_dominatrix", "role_escort",
    "role_foreigner", "role_ghost", "role_housewife", "role_idol", "role_magical_girl", "role_maid",
    "role_massagist", "role_miko", "role_mythical_being", "role_neet", "role_nekomimi", "role_newlywed",
    "role_ninja", "role_normal", "role_nun", "role_nurse", "role_office_lady", "role_other", "role_police",
    "role_priest", "role_princess", "role_queen", "role_school_nurse", "role_scientist", "role_sorcerer",
    "role_student", "role_succubus", "role_teacher", "role_tomboy", "role_tutor", "role_waitress",
    "role_warrior", "role_witch",

    "relationship_acquaintance", "relationship_anothers_girlfriend",
    "relationship_anothers_wife", "relationship_aunt", "relationship_babysitter", "relationship_childhood_friend",
    "relationship_classmate", "relationship_cousin", "relationship_customer", "relationship_daughter",
    "relationship_daughter-in-law", "relationship_employee", "relationship_employer", "relationship_enemy",
    "relationship_fiance", "relationship_friend", "relationship_friends_daughter", "relationship_friends_girlfriend",
    "relationship_friends_mother", "relationship_friends_sister", "relationship_friends_wife",
    "relationship_girlfriend", "relationship_landlord", "relationship_manager", "relationship_master",
    "relationship_mother", "relationship_mother-in-law", "relationship_neighbor", "relationship_niece",
    "relationship_none", "relationship_older_sister", "relationship_patient", "relationship_pet",
    "relationship_physician", "relationship_relative", "relationship_relatives_friend",
    "relationship_relatives_girlfriend", "relationship_relatives_wife", "relationship_servant",
    "relationship_server", "relationship_sister-in-law", "relationship_slave", "relationship_stepdaughter",
    "relationship_stepmother", "relationship_stepsister", "relationship_stranger", "relationship_student",
    "relationship_teacher", "relationship_tutee", "relationship_tutor", "relationship_twin",
    "relationship_underclassman", "relationship_upperclassman", "relationship_wife", "relationship_workmate",
    "relationship_younger_sister",

    "maleBody_adult", "maleBody_animal", "maleBody_animal_ears",
    "maleBody_bald", "maleBody_beard", "maleBody_dark_skin", "maleBody_elderly", "maleBody_exaggerated_penis",
    "maleBody_fat", "maleBody_goatee", "maleBody_hairy", "maleBody_half_animal", "maleBody_horns",
    "maleBody_large_penis", "maleBody_long_hair", "maleBody_middle_age", "maleBody_monster", "maleBody_muscular",
    "maleBody_mustache", "maleBody_none", "maleBody_short", "maleBody_short_hair", "maleBody_skinny",
    "maleBody_small_penis", "maleBody_tail", "maleBody_tall", "maleBody_tanned", "maleBody_tan_line",
    "maleBody_teenager", "maleBody_wings", "maleBody_young",

    "femaleBody_adult", "femaleBody_animal_ears",
    "femaleBody_chubby", "femaleBody_dark_skin", "femaleBody_elderly", "femaleBody_elf_ears",
    "femaleBody_exaggerated_breasts", "femaleBody_fat", "femaleBody_hairy", "femaleBody_hair_bun",
    "femaleBody_half_animal", "femaleBody_halo", "femaleBody_hime_cut", "femaleBody_horns",
    "femaleBody_large_breasts", "femaleBody_long_hair", "femaleBody_middle_age", "femaleBody_muscular",
    "femaleBody_none", "femaleBody_pigtails", "femaleBody_ponytail", "femaleBody_short", "femaleBody_short_hair",
    "femaleBody_skinny", "femaleBody_small_breasts", "femaleBody_tail", "femaleBody_tall", "femaleBody_tanned",
    "femaleBody_tan_line", "femaleBody_teenager", "femaleBody_twintails", "femaleBody_wings", "femaleBody_young",

    "grouping_foursome_(1_female)", "grouping_foursome_(1_male)", "grouping_foursome_(mixed)",
    "grouping_foursome_(only_female)", "grouping_one_on_one", "grouping_one_on_one_(2_females)",
    "grouping_one_on_one_(2_males)", "grouping_orgy_(1_female)", "grouping_orgy_(1_male)",
    "grouping_orgy_(mainly_female)", "grouping_orgy_(mainly_male)", "grouping_orgy_(mixed)",
    "grouping_orgy_(only_female)", "grouping_orgy_(only_male)", "grouping_solo_(female)",
    "grouping_solo_(male)", "grouping_threesome_(1_female)", "grouping_threesome_(1_male)",
    "grouping_threesome_(only_female)", "grouping_threesome_(only_male)",

    "scene_adultery", "scene_ahegao", "scene_anal_(female)", "scene_anal_(male)", "scene_aphrodisiac", "scene_armpit_sex",
    "scene_asphyxiation", "scene_blackmail", "scene_blowjob", "scene_bondage", "scene_breast_feeding",
    "scene_breast_sucking", "scene_bukkake", "scene_cheating_(female)", "scene_cheating_(male)",
    "scene_chikan", "scene_clothed_sex", "scene_consensual", "scene_cunnilingus", "scene_defloration",
    "scene_discipline", "scene_dominance", "scene_double_penetration", "scene_drunk", "scene_enema",
    "scene_exhibitionism", "scene_facesitting", "scene_fingering_(female)", "scene_fingering_(male)",
    "scene_fisting", "scene_footjob", "scene_grinding", "scene_groping", "scene_handjob", "scene_humiliation",
    "scene_hypnosis", "scene_intercrural", "scene_interracial_sex", "scene_interspecies_sex", "scene_lactation",
    "scene_lotion", "scene_masochism", "scene_masturbation", "scene_mind_break", "scene_nonhuman", "scene_orgy",
    "scene_paizuri", "scene_phone_sex", "scene_props", "scene_rape", "scene_reverse_rape", "scene_rimjob",
    "scene_sadism", "scene_scat", "scene_sex_toys", "scene_spanking", "scene_squirt", "scene_submission",
    "scene_sumata", "scene_swingers", "scene_tentacles", "scene_voyeurism", "scene_watersports",
    "scene_x-ray_blowjob", "scene_x-ray_sex",

    "position_69", "position_acrobat", "position_arch", "position_bodyguard", "position_butterfly", "position_cowgirl",
    "position_dancer", "position_deck_chair", "position_deep_stick", "position_doggy", "position_drill",
    "position_ex_sex", "position_jockey", "position_lap_dance", "position_leg_glider", "position_lotus",
    "position_mastery", "position_missionary", "position_none", "position_other", "position_pile_driver",
    "position_prison_guard", "position_reverse_piggyback", "position_rodeo", "position_spoons", "position_standing",
    "position_teaspoons", "position_unusual", "position_victory"
]
