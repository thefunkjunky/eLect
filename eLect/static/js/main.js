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
    this.viewItem = {title: "Welcome to eLect!",
                    description_short: "Online elections platform.",
                    category: "",
                };

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

    if (this.currentViewCategory = "election") {
        console.log("if currentview = election has been called.");
        $("#action-add").css("align-items", "center");
    };
}

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


eLect.prototype.onItemClicked = function(event) {
    console.log("onItemClicked called");
    var item = $(event.target);
    var category = item.attr("category");
    console.log("onItemClicked item:", item);
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



eLect.prototype.getObject = function(category, objectURL, callback) {
    var ajax = $.ajax(objectURL, {
        type: 'GET',
        dataType: 'json'
    });
    ajax.done(this.onGetObjectDone.bind(this, category, callback));
    ajax.fail(this.onFail.bind(this, "Getting parent object information"));
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


eLect.prototype.getResponseList = function(category, listURL) {
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
    }
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

    // Goes last, to ensure all clickable things are made clicky
    this.clickActionBehavior();
};

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