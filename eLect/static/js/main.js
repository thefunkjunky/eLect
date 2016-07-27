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
    this.currentViewCategory = "home";
    this.listURL = "/api/elections";
    this.parentItem = null;
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

    this.formResponseList = $(".form-response-list");

    this.formResponseListCheckbox = $(".item-form-select");

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
    this.deleteItemModalSource = $("#delete-modal-template").html();
    this.deleteItemModalTemplate = Handlebars.compile(this.deleteItemModalSource);



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
    this.addItem.click(this.onAddItemClicked.bind(this, "POST"));

    this.actionViewElections = $("#action-view-elections");
    this.actionViewElections.click(this.onElectionsButtonClicked.bind(this));


    this.editItem = $(".item-edit");
    this.editItem.click(this.onAddItemClicked.bind(this, "PUT"));

    this.deleteItems = $("#button-delete");
    this.deleteItems.click(this.onDeleteItemsClicked.bind(this));

    if (this.candidateSelect.length > 0) {
        this.candidateSelect.click(this.onCandidateSelected.bind(this));
    };

    this.voteButton = $("#button-vote");
    this.voteButton.click(this.onVoteButtonClicked.bind(this));

    // console.log($("#responses"));
    // $("#responses").on("click", ".item-title",
    //     this.onItemClicked.bind(this));

    // Should be the last function to run after page has loaded and jquery objects assigned
    this.finalRenderCleanup();

};

eLect.prototype.finalRenderCleanup = function() {
    if (this.currentViewCategory == "home") {
        this.deleteItems.hide();
        this.addItem.hide();
    } else {
        this.actionViewElections.hide();
        this.addItem.show();
    }
};

eLect.prototype.updateNavBar = function() {
    election = this.election;
    race = this.race;
    candidate = this.candidate;
    var context = {election:election, race:race, candidate:candidate};
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
    var listURL = "/api/races/" + this.race.id + "/candidates";
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

    var centerModal = $(this.fullDescrModalTemplate(context));
    this.centerModal.replaceWith(centerModal);
    this.centerModal = centerModal;

    this.viewItem = this.parentObject;

    this.centerModal.css("display", "block");

    this.centerModalClose = $(".modal-close");
    this.centerModalClose.click(this.onCenterModalCloseClicked.bind(this));

}

eLect.prototype.onAddItemClicked = function(method, event) {
    var item = $(event.target);
    var category = this.currentViewCategory;
    var itemID = item.attr("data-id");
    var categoryCapitalized = this.capitalize(category);
    
    if (method=="POST") {
        var title = "Add " + categoryCapitalized;
        var context = {
            title: title,
            titleValue: "Title",
            shortValue: "Short Description",
            longValue: "Long Description",
        };

        var centerModal = $(this.addItemModalTemplate(context));
        this.centerModal.replaceWith(centerModal);
        this.centerModal = centerModal;

        this.centerModal.css("display", "block");

        this.centerModalClose = $(".modal-close");
        this.centerModalClose.click(this.onCenterModalCloseClicked.bind(this));

        this.addItemForm = $("#form-add-item");

        this.itemSubmit = $("#form-submit");
        this.itemSubmit.click(this.onItemSubmitClicked.bind(this, method));

    } else if (method=="PUT") {
        var getURL = "/api/" + category + "s" + "/" + itemID;
        $.getJSON(getURL).done(data => {
            var title = "Edit " + categoryCapitalized;
            var context = {
                title: title,
                titleValue: data.title,
                shortValue: data.description_short,
                longValue: data.description_long,
            };
            var centerModal = $(this.addItemModalTemplate(context));
            this.centerModal.replaceWith(centerModal);
            this.centerModal = centerModal;

            this.centerModal.css("display", "block");

            this.centerModalClose = $(".modal-close");
            this.centerModalClose.click(this.onCenterModalCloseClicked.bind(this));

            this.addItemForm = $("#form-add-item");

            this.itemSubmit = $("#form-submit");
            console.log("data.id", data.id);
            this.itemSubmit.click(this.onItemSubmitClicked.bind(this, "PUT", data.id));

        }).fail(this.onCenterModalCloseClicked.bind(this));
    };
};

eLect.prototype.onItemSubmitClicked = function(method, id, event) {
    // var categories = ["election", "race", "candidate"];
    // var nextCatIndex = categories.indexOf(this.category) + 1;
    // var nextCategory = categories[nextCatIndex];
    var postURL = "/api/" + this.currentViewCategory + "s";
    var putURL = postURL;
    // var addItemData = new FormData(this.addItemForm[0]);
    if (method=="POST") {
        this.postObject(postURL, "POST");
    } else if (method=="PUT") {
        this.postObject(putURL, "PUT", id);
    };
};

eLect.prototype.onDeleteItemsClicked = function(event) {
    console.log("delete button clicked");
    var context = {
        title: "Delete item(s)",
        description: "Are you sure you want to delete selected items(s) ?",
    }
    var centerModal = $(this.deleteItemModalTemplate(context));
    this.centerModal.replaceWith(centerModal);
    this.centerModal = centerModal;

    this.centerModal.css("display", "block");

    this.responsesForm = $("#form-response-list");
    this.responsesChecked = $(".item-form-select:checked");

    console.log("this.responsesChecked", this.responsesChecked);

    this.itemDeleteSubmit = $("#form-submit");
    this.itemDeleteSubmit.click(this.onItemDeleteSubmitClicked.bind(this));

    this.centerModalClose = $(".modal-close");
    this.centerModalClose.click(this.onCenterModalCloseClicked.bind(this));
};

eLect.prototype.onItemDeleteSubmitClicked = function(event) {
    // $.when() waits for all refererd objects to be returned before executing then()
    $.when(
        // iterates through all check objects and deletes each one
        $.each(this.responsesChecked, (key, value) => {
            var itemID = $(value).attr("data-id");
            var deleteURL = "/api/" + this.currentViewCategory + "s";
            var data = {
                id: parseInt(itemID),
            };
            $.ajax(deleteURL, {
            type: 'DELETE',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify(data),
            }).fail(this.onFail.bind(this, "DELETE failed..."));
        })).then(this.onPostObjectDone.bind(this));
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
        this.parentObject = this.viewItem;
        var objectURL = "/api/candidates/" + item.attr("data-id");
        this.getObject(category, objectURL, this.onRenderCenterModal);
    };
}


eLect.prototype.onItemClicked = function(event) {
    var item = $(event.target);
    this.selectView(item);
};

eLect.prototype.onNavItemClicked = function(event) {
    var item = $(event.target);
    category = item.attr("category");
    if (category == "election") {
        var objectURL = "/api/elections/" + item.attr("data-id");
        this.getObject(category, objectURL, this.onRenderCenterModal);
    } else if (category == "race") {
        this.parentObject = this.viewItem;
        var objectURL = "/api/races/" + item.attr("data-id");
        this.getObject(category, objectURL);
        // Update the category for the list objects
        category = "candidate";
        var listURL = "/api/races/" + item.attr("data-id") + "/candidates";
        this.getObject(category, objectURL, this.onRenderCenterModal);
    } else if (category == "candidate") {
        this.parentObject = this.viewItem;
        var objectURL = "/api/candidates/" + item.attr("data-id");
        this.getObject(category, objectURL, this.onRenderCenterModal);
    };
};

eLect.prototype.onCandidateSelected = function(event) {
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
    });
    var selectedItem = $(".response-item")[selectedItemIndex];
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

eLect.prototype.alreadyVoted = function(voteURL, response, race, callback) {
    $.getJSON(voteURL).done(function(data){
            response.alreadyvoted = true;
            if (race) {
            race.alreadyvoted = true;
            };
        }).fail(function() {
            response.alreadyvoted = false;
            if (race) {
            race.alreadyvoted = false;
            };
        }).always(function () {
            callback.bind(this)(response, race);
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

// eLect.prototype.getVote = function(response, candID, callback) {
//     var raceID = response.id;
//     callback.bind(this);
//     if (raceID) {
//         var voteURL = "/api/races/" + raceID + "/votes/user/" + this.userID;
//     } else if (candID) {
//         var voteURL = "/api/candidates/" + candID + "/votes/user/" + this.userID;
//     }
//     var ajax = $.ajax(voteURL, {
//         type: 'GET',
//         dataType: 'json',
//     });
//     // ajax.done(this.onGetVoteDone.bind(this, callback));
//     ajax.fail(this.onFail.bind(this, "Getting vote object information"));

//     // if (ajax.responseJSON) {
//     //     return ajax.responseJSON;
//     // } else {
//     //     return null;
//     // };
//     // console.log("ajax", ajax);
//     // console.log("ajax.responseJSON", ajax.responseJSON);

//     return ajax.done(function(data, callback){
//         if (data) {
//             console.log("callback, data", callback, data);
//             return [data, callback];
//         } else {
//             return null;
//         }
//     });
// };

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

    this.viewItem
};

eLect.prototype.onGetVoteDone = function(callback, data) {
    // send a this.checkVote as callback to work
    if (callback) {
        var isVote = callback.bind(this)(data);
        console.log("isVote", isVote);
        return isVote;
    };
    return data;
};

eLect.prototype.getResponseList = function(category, listURL) {
    this.listURL = listURL;
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

    for (i in this.responses) {
        this.responses[i].category = category;
        this.responses[i].index = i;

        if (this.currentViewCategory == "race") {
            this.viewItem = this.election;
            var voteURL = '/api/races/'+this.responses[i].id + '/votes/user/' + this.userID;
            this.alreadyVoted(voteURL, this.responses[i], null, this.modifyViewItem);
            console.log("final this.response", this.responses[i]);
        } else if (this.currentViewCategory == "candidate") {
            this.viewItem = this.race;
            var voteURL = '/api/candidates/'+this.responses[i].id + '/votes/user/' + this.userID;
            this.alreadyVoted(voteURL, this.responses[i], this.race, this.modifyViewItem);
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

eLect.prototype.postObject = function(postURL, method, putID) {
    var data = this.convertFormToJSON("#form-add-item");
    if (this.race) {
        data["race_id"] = this.race.id;
    } else if (this.election) {
        data["election_id"] = this.election.id;
    }; 
    if (putID) {
        data["id"] = parseInt(putID);
    };
    console.log("post data", data);
    var ajax = $.ajax(postURL, {
        type: method,
        // cache: false,
        contentType: "application/json; charset=utf-8",
        // processData: false,
        dataType: 'json',
        data: JSON.stringify(data),
    });
    ajax.done(this.onPostObjectDone.bind(this));
    ajax.fail(this.onFail.bind(this, "POST failed...")); 
};

eLect.prototype.putObject = function(putURL) {
    var data = this.convertFormToJSON("#form-add-item");
    console.log("put data", data);
    var ajax = $.ajax(putURL, {
        type: 'PUT',
        // cache: false,
        contentType: "application/json; charset=utf-8",
        // processData: false,
        dataType: 'json',
        data: JSON.stringify(data),
    });
    ajax.done(this.onPostObjectDone.bind(this));
    ajax.fail(this.onFail.bind(this, "PUT failed..."));
}

eLect.prototype.postVote = function(voteData, postURL) {
    console.log("voteData", voteData);
    var data = voteData;
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

eLect.prototype.modifyViewItem = function(response, race) {
    var viewResponses = $(".response-item");
    if (race && race.alreadyvoted==true) {
        $(viewResponses).animate({backgroundColor: "#cc7066"});
    } else if (response.alreadyvoted == true) {
        $(viewResponses[response.index]).animate({backgroundColor: "#cc7066"});
    };
};

eLect.prototype.onFail = function(what, event) {
    // Called when an AJAX call fails
    console.error(what, "failed: ", event.statusText);
};

// Init page w/ eLect class
$(document).ready(function() {
    window.app = new eLect();
});