Handlebars.registerHelper('if_equal', function(a, b, opts) {
    if (a == b) {
        return opts.fn(this);
    } else {
        return opts.inverse(this);
    }
});

var eLect = function() {
    this.election = null;
    this.race = null;
    this.candidate = null;
    this.currentViewCategory = "election";
    this.listURL = "/api/elections";
    this.viewItem = {title: "Welcome to eLect!",
                    description_short: "Online elections platform.",
                    category: "",
                };
    this.candidateSelect = [];
    this.userID = 1;

    this.clickActionBehavior();

    this.mainNavBar = $("#nav-bar");
    this.navbarSource = $("#main-nav-bar-template").html();
    this.navbarTemplate = Handlebars.compile(this.navbarSource);

    this.viewTitleBar = $("#view-bar");
    this.viewTitleBarSource = $("#view-title-template").html();
    this.viewTitleBarTemplate = Handlebars.compile(this.viewTitleBarSource);

    this.viewActions = $("#view-actions");
    this.viewActionsSource = $("#action-buttons-template").html();
    this.viewActionsTemplate = Handlebars.compile(this.viewActionsSource);

    this.responseList = $("#response-list");
    this.responseListSource = $("#response-list-template").html();
    this.responseListTemplate = Handlebars.compile(this.responseListSource);
    this.responses = [];

    this.bottomActions = $("#bottom-actions");
    this.bottomActionsSource = $("#bottom-actions-template").html();
    this.bottomActionsTemplate = Handlebars.compile(this.bottomActionsSource);


    this.centerModal = $("#modal");
    this.fullDescrModalSource = $("#full-descr-template").html();
    this.fullDescrModalTemplate = Handlebars.compile(this.fullDescrModalSource);
    this.addItemModalSource = $("#add-item-template").html();
    this.addItemModalTemplate = Handlebars.compile(this.addItemModalSource);



    // this.viewTitle = $("#view-title");
    // this.viewDescription = $("#view-description");


    // $("#item-title").on("click", "#item-title",
    //     this.onItemClicked.bind(this));

    // this.get_elections();
    this.renderViewTitleBar();
    this.updateNavBar();
    this.renderViewActions();
    this.renderBottomActions();

    
    this.clickActionBehavior();
};

eLect.prototype.clickActionBehavior = function() {
    this.electionsButton = $("#nav-elections");
    this.electionsButton.click(this.onElectionsButtonClicked.bind(this));
    this.navElection = $("#nav-election");
    // this.electionsButton.click(this.onElectionButtonClicked.bind(this));

    this.racesButton = $("#nav-races");
    this.racesButton.click(this.onRacesButtonClicked.bind(this));
    this.navRace = $("#nav-race");
    // this.racesButton.click(this.onRaceButtonClicked.bind(this));

    this.candidatesButton = $("#nav-candidates");
    this.candidatesButton.click(this.onCandidatesButtonClicked.bind(this));
    this.navCandidate = $("#nav-candidate");
    // this.candidatesButton.click(this.onCandidateButtonClicked.bind(this));

    this.viewItemTitleLink = $(".item-title");
    this.viewItemTitleLink.click(this.onItemClicked.bind(this));

    this.navItem = $(".nav-item");
    this.navItem.click(this.onNavItemClicked.bind(this));

    this.addItem = $("#action-add");
    this.addItem.click(this.onAddItemClicked.bind(this));

    console.log("this.candidateSelect.length", this.candidateSelect.length);
    if (this.candidateSelect.length > 0) {
        this.candidateSelect.click(this.onCandidateSelected.bind(this));
        console.log("this.candidateSelect.click assigned");
    };

    this.voteButton = $("#button-vote");
    this.voteButton.click(this.onVoteButtonClicked.bind(this));

    // console.log($("#responses"));
    // $("#responses").on("click", ".item-title",
    //     this.onItemClicked.bind(this));

};

eLect.prototype.updateNavBar = function() {
    election = this.election;
    race = this.race;
    candidate = this.candidate;
    var context = {election:election, race:race, candidate:candidate};
    console.log(context);
    var mainNavBar = $(this.navbarTemplate(context));
    this.mainNavBar.replaceWith(mainNavBar);
    this.mainNavBar = mainNavBar;
    if (!election) {
        this.electionsButton.show();
        this.navElection.hide();
        this.racesButton.hide();
        this.navRace.hide();
        this.candidatesButton.hide();
        this.navCandidate.hide();
    } else if (election) {
        this.electionsButton.show();
        this.navElection.show();
        this.racesButton.show();
        this.navRace.hide();
        this.candidatesButton.hide();
        this.navCandidate.hide();
    } else if (race) {
        this.electionsButton.show();
        this.navElection.show();
        this.racesButton.show();
        this.navRace.show();
        this.candidatesButton.show();
        this.navCandidate.hide();
    } else if (candidate) {
        this.electionsButton.show();
        this.navElection.show();
        this.racesButton.show();
        this.navRace.show();
        this.candidatesButton.show();
        this.navCandidate.show();
    };
    this.clickActionBehavior();
};

eLect.prototype.renderViewTitleBar = function() {
    // var category = category;
    // var categoryFormatted = category.charAt(0).toUpperCase() + category.slice(1);
    // var title = categoryFormatted + ": " + this.viewItem.title;
    var context = {title: this.viewItem.title, 
        description: this.viewItem.description_short};
    var viewTitleBar = $(this.viewTitleBarTemplate(context));
    this.viewTitleBar.replaceWith(viewTitleBar);
    this.viewTitleBar = viewTitleBar;
};

eLect.prototype.renderViewActions = function() {
    var context = {
        category: this.currentViewCategory,
        parentID: this.viewItem.id
    };
    var viewActions = $(this.viewActionsTemplate(context));
    this.viewActions.replaceWith(viewActions);
    this.viewActions = viewActions;
};

eLect.prototype.renderBottomActions = function() {
    var context = {
        category: this.currentViewCategory,
    };
    var bottomActions = $(this.bottomActionsTemplate(context));
    this.bottomActions.replaceWith(bottomActions);
    this.bottomActions = bottomActions;
};

eLect.prototype.onElectionsButtonClicked = function(event) {
    var category = "election";
    var listURL = "/api/elections";
    this.election = null;
    this.race = null;
    this.candidate = null;
    this.viewItem = {title: "Elections", 
        description_short: "Current list of open elections"};
    this.getResponseList(category, listURL);
};

eLect.prototype.onRacesButtonClicked = function(event) {
    var category = "race";
    var listURL = "/api/elections/" + this.election.id + "/races";
    this.race = null;
    this.candidate = null;
    this.getResponseList(category, listURL);
};

eLect.prototype.onCandidatesButtonClicked = function(event) {
    var category = "candidate";
    var listURL = "/api/races/" + this.race.id + "/candidates/";
    this.candidate = null;
    this.getResponseList(category, listURL);
};

eLect.prototype.capitalize = function(string) {
    string[0] = string[0].toUpperCase();
    return string;
}


eLect.prototype.onRenderCenterModal = function() {
    var context = {
        title: this.viewItem.title,
        icon_small_location: this.viewItem.icon_small_location,
    };
    if (this.viewItem.description_long) {
        context.description = this.viewItem.description_long;
    } else {
        context.description = this.viewItem.description_short;
    };
    console.log("onRenderCenterModal context: ", context);

    var centerModal = $(this.fullDescrModalTemplate(context));
    this.centerModal.replaceWith(centerModal);
    this.centerModal = centerModal;

    this.centerModal.css("display", "block");

    this.centerModalClose = $(".modal-close");
    this.centerModalClose.click(this.onCenterModalCloseClicked.bind(this));

}

eLect.prototype.onAddItemClicked = function(event) {
    var item = $(event.target);
    var category = item.attr("category");
    var categoryCapitalized = this.capitalize(category);
    var title = "Add " + categoryCapitalized;
    var context = {
        title: title,
        category: category,
    };

    var centerModal = $(this.addItemModalTemplate(context));
    this.centerModal.replaceWith(centerModal);
    this.centerModal = centerModal;

    this.centerModal.css("display", "block");

    this.centerModalClose = $(".modal-close");
    this.centerModalClose.click(this.onCenterModalCloseClicked.bind(this));

    this.addItemForm = $("#form-add-item");


    this.addItemSubmit = $("#form-submit");
    this.addItemSubmit.click(this.onAddItemSubmitClicked.bind(this));
};

eLect.prototype.onAddItemSubmitClicked = function(event) {
    // var categories = ["election", "race", "candidate"];
    // var nextCatIndex = categories.indexOf(this.category) + 1;
    // var nextCategory = categories[nextCatIndex];
    var postURL = "/api/" + this.currentViewCategory + "s";
    console.log("postURL", postURL);
    // var addItemData = new FormData(this.addItemForm[0]);
    this.postObject(postURL);
};

eLect.prototype.onCenterModalCloseClicked = function(event) {
    this.centerModal.css("display", "none");
}

// When the user clicks anywhere outside of the modal, close it
// window.onclick = function(event) {
//     if (event.target == this.centerModal) {
//         this.centerModal.css("display", "none");
//     };
// };

eLect.prototype.selectView = function (item) {
    var category = item.attr("category");
    if (category == "election") {
        var objectURL = "/api/elections/" + item.attr("data-id");
        this.getObject(category, objectURL);
        // Update the category for the list objects
        category = "race";
        var listURL = "/api/elections/" + item.attr("data-id") + "/races";
        this.getResponseList(category, listURL);
    } else if (category == "race") {
        var objectURL = "/api/races/" + item.attr("data-id");
        this.getObject(category, objectURL);
        // Update the category for the list objects
        category = "candidate";
        var listURL = "/api/races/" + item.attr("data-id") + "/candidates";
        this.getResponseList(category, listURL);
    } else if (category == "candidate") {
        var objectURL = "/api/candidates/" + item.attr("data-id");
        this.getObject(category, objectURL, this.onRenderCenterModal);
    };
}


eLect.prototype.onItemClicked = function(event) {
    console.log("onItemClicked called");
    var item = $(event.target);
    console.log("onItemClicked item:", item);
    this.selectView(item);
};

eLect.prototype.onNavItemClicked = function(event) {
    console.log("onNavItemClicked called");
    var item = $(event.target);
    category = item.attr("category");
    console.log("onItemClicked item:", item);
    if (category == "election") {
        var objectURL = "/api/elections/" + item.attr("data-id");
        this.getObject(category, objectURL, this.onRenderCenterModal);
    } else if (category == "race") {
        var objectURL = "/api/races/" + item.attr("data-id");
        this.getObject(category, objectURL);
        // Update the category for the list objects
        category = "candidate";
        var listURL = "/api/races/" + item.attr("data-id") + "/candidates";
        this.getObject(category, objectURL, this.onRenderCenterModal);
    } else if (category == "candidate") {
        var objectURL = "/api/candidates/" + item.attr("data-id");
        this.getObject(category, objectURL, this.onRenderCenterModal);
    };
};

eLect.prototype.onCandidateSelected = function(event) {
    console.log("onSelected");
    var item = $(event.target);
    var itemDataId = item.attr("data-id");
    var selectedItemIndex = item.attr("index");
    // var defaultClasses = $(".response-item").attr("class");
    // unselectedClasses = defaultClasses + " response-item-unselected";
    // console.log("unselectedClasses", unselectedClasses);
    $(".response-item").each(function(index, element) {
        if (index != selectedItemIndex) {
            $(element).addClass("response-item-unselected");
            $(element).itemID = null;
            // $(element).css("opacity", '70%');
            // $(element).fadeTo(600,0.3);
            $(element).animate({backgroundColor: "#412825"});
        };
        console.log("response-item", index, element);
    });
    var selectedItem = $(".response-item")[selectedItemIndex];
    console.log("selectedItem", selectedItem);
    console.log("itemDataId", itemDataId);
    selectedItem.id = "selected-response";
    selectedItem.value = 1;
    console.log("selected response", selectedItem);
    // $(selectedItem).fadeTo(600,1);
    // $(selectedItem).css("background-color", "#804e49");
    $(selectedItem).animate({backgroundColor: "#804e49"});
    // $(selectedItem).css("opacity", "100%");
    // $(".response-item")[item.attr("index")].removeClass("response-item-unselected");
    // item.selected = "true"
    // $(item).css("class", defaultClasses);
        // $(this.candidateSelect[i]).css("class", defaultClasses + " response-item-unselected");
    // $(item).css("class", defaultClasses);
};

eLect.prototype.alreadyVoted = function(voteURL, response) {
    $.getJSON(voteURL).done(function(data){
            response.alreadyvoted = "true";
        }).fail(function() {
            response.alreadyvoted = "false";
        });
};



eLect.prototype.onVoteButtonClicked = function(event) {
    var item = $(event.target);
    var selectedResponse = $("#selected-response");
    var candidateID = parseInt(selectedResponse.attr("data-id"));
    var value = parseInt(selectedResponse.attr("value"));
    var voteData = {
        value: value,
        candidate_id: candidateID,
        user_id: this.userID,
    };
    var postURL = "/api/votes"
    this.postVote(voteData, postURL);
};

eLect.prototype.returnData = function(data) {
    console.log("return data", data);
    return data;
};

eLect.prototype.getObject = function(category, objectURL, callback) {
    var ajax = $.ajax(objectURL, {
        type: 'GET',
        dataType: 'json'
    });
    ajax.done(this.onGetObjectDone.bind(this, category, callback));
    ajax.fail(this.onFail.bind(this, "Getting object information"));
};

eLect.prototype.getVote = function(response, candID, callback) {
    var raceID = response.id;
    console.log("getvote callback", callback);
    callback.bind(this);
    if (raceID) {
        var voteURL = "/api/races/" + raceID + "/votes/user/" + this.userID;
    } else if (candID) {
        var voteURL = "/api/candidates/" + candID + "/votes/user/" + this.userID;
    }
    var ajax = $.ajax(voteURL, {
        type: 'GET',
        dataType: 'json',
    });
    // ajax.done(this.onGetVoteDone.bind(this, callback));
    ajax.fail(this.onFail.bind(this, "Getting vote object information"));

    // if (ajax.responseJSON) {
    //     return ajax.responseJSON;
    // } else {
    //     return null;
    // };
    // console.log("ajax", ajax);
    // console.log("ajax.responseJSON", ajax.responseJSON);

    return ajax.done(function(data, callback){
        if (data) {
            console.log("callback, data", callback, data);
            return [data, callback];
        } else {
            return null;
        }
    });
};

eLect.prototype.onGetObjectDone = function(category, callback, data) {
    console.log(category);
    console.log("callback: ", callback);
    if (category == "election"){
        this.election = data;
        console.log(this.election);
    } else if (category == "race"){
        this.race = data;
        console.log(this.race);
    } else if (category == "candidate"){
        this.candidate = data;
        console.log(this.candidate);
    };
    this.viewItem = data;
    console.log("this.viewItem: ", this.viewItem);
    
    if (callback) {
        callback.bind(this)();
    };
};

eLect.prototype.onGetVoteDone = function(callback, data) {
    // send a this.checkVote as callback to work
    console.log("getVote callbackDone", callback);
    if (callback) {
        var isVote = callback.bind(this)(data);
        console.log("isVote", isVote);
        return isVote;
    };
    return data;
};

eLect.prototype.getResponseList = function(category, listURL) {
    this.listURL = listURL;
    console.log("listURL", this.listURL);
    var ajax = $.ajax(listURL, {
        type: 'GET',
        dataType: 'json'
    });
    ajax.done(this.onGetResponsesDone.bind(this, category));
    ajax.fail(this.onFail.bind(this, "Getting responses information"));
};


eLect.prototype.onGetResponsesDone = function(category, data) {
    this.responses = data;
    this.currentViewCategory = category;

    console.log("currentViewCategory: " + this.currentViewCategory);
    for (i in this.responses) {
        console.log("response # " + i + ":" + this.responses[i]);
        this.responses[i].category = category;
        this.responses[i].index = i;

        if (this.currentViewCategory == "race") {
            var voteURL = '/api/races/'+this.responses[i].id + '/votes/user/' + this.userID;
            this.alreadyVoted(voteURL, this.responses[i]);
            console.log("final this.response", this.responses[i]);
        } else if (this.currentViewCategory == "candidate") {
            var voteURL = '/api/candidates/'+this.responses[i].id + '/votes/user/' + this.userID;
            this.alreadyVoted(voteURL, this.responses[i]);
            console.log("final this.response", this.responses[i]);
        };
    };
    // var categoryList = {
    //     category: category
    // };
    // console.log(categoryList);
    // this.responses = $(this.responses).map(function(obj) {
    //     $.extend(this.responses, category);
    // });
    // this.responses = $.merge(responses, categoryList);

    // var categoryFormatted = category.charAt(0).toUpperCase() + category.slice(1);
    // var title = categoryFormatted + ": " + this.viewItem.title;
    // this.viewItem = {title: title, 
    //     description: this.viewItem.description};
    console.log("this.viewItem: ", this.viewItem);

    console.log(this.responses);
    this.renderViewTitleBar();
    this.updateViewItems();
    this.updateNavBar();
    this.renderViewActions();
    this.renderBottomActions();

    this.candidateSelect = $(".candidate-select");
    console.log("this.candidateSelect", this.candidateSelect);
    // Goes last, to ensure all clickable things are made clicky
    this.clickActionBehavior();
};

eLect.prototype.convertFormToJSON = function(form) {
    var array = $(form).serializeArray();
    var json = {};
    
    $.each(array, function() {
        json[this.name] = this.value || '';
    });
    
    return json;
};

eLect.prototype.postObject = function(postURL) {
    var data = this.convertFormToJSON("#form-add-item");
    if (this.race) {
        data["race_id"] = this.race.id;
    } else if (this.election) {
        data["election_id"] = this.election.id;
    };
    console.log("post data", data);
    var ajax = $.ajax(postURL, {
        type: 'POST',
        // cache: false,
        contentType: "application/json; charset=utf-8",
        // processData: false,
        dataType: 'json',
        data: JSON.stringify(data),
    });
    ajax.done(this.onPostObjectDone.bind(this));
    ajax.fail(this.onFail.bind(this, "POST failed...")); 
};

eLect.prototype.postVote = function(voteData, postURL) {
    console.log("voteData", voteData);
    var data = voteData;
    console.log("data json stringified", JSON.stringify(data));
    var ajax = $.ajax(postURL, {
        type: 'POST',
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        data: JSON.stringify(data),
    });
    ajax.done(this.onPostVoteDone.bind(this));
    ajax.fail(this.onFail.bind(this, "POST failed...")); 
};

eLect.prototype.onPostObjectDone = function() {
    this.onCenterModalCloseClicked();
    this.getResponseList(this.currentViewCategory, this.listURL);
};

eLect.prototype.onPostVoteDone = function() {
    this.racesButton.click();
}


eLect.prototype.updateViewItems = function() {
    var context = {
            responses: this.responses
    };
    var responseList = $(this.responseListTemplate(context));
    this.responseList.replaceWith(responseList);
    this.responseList = responseList;
};

eLect.prototype.onFail = function(what, event) {
    // Called when an AJAX call fails
    console.error(what, "failed: ", event.statusText);
};

$(document).ready(function() {
    window.app = new eLect();
});