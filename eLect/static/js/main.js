var eLect = function() {
    this.electionsButton = $("#nav-elections");
    this.electionsButton.click(this.onElectionsButtonClicked.bind(this));
    // this.electionsButton = $("#nav-election");
    // this.electionsButton.click(this.onElectionButtonClicked.bind(this));

    this.racesButton = $("#nav-races");
    this.racesButton.click(this.onRacesButtonClicked.bind(this));
    // this.racesButton = $("#nav-race");
    // this.racesButton.click(this.onRaceButtonClicked.bind(this));

    this.candidatesButton = $("#nav-candidates");
    this.candidatesButton.click(this.onCandidatesButtonClicked.bind(this));
    // this.candidatesButton = $("#nav-candidate");
    // this.candidatesButton.click(this.onCandidateButtonClicked.bind(this));

    this.navbarSource = $("#main-nav-bar-template").html();
    this.navbarTemplate = Handlebars.compile(this.navbarSource);

    this.responseList = $("#response-list");
    this.responseSource = $("#response-item-template").html();
    this.responseListTemplate = Handlebars.compile(this.responseSource);
    this.responses = [];

    this.viewTitle = $("#view-title");
    this.viewDescription = $("#view-description");

    $("#responses").on("click", "#item-title",
        this.onItemClicked.bind(this));

    this.get_elections();
};

eLect.prototype.onElectionsButtonClicked = function(event) {
    this.get_elections();
};

eLect.prototype.onItemClicked = function(event) {
    var item = $(event.target);
};

eLect.prototype.get_elections = function() {
    var ajax = $.ajax('/api/elections', {
        type: 'GET',
        dataType: 'json'
    });
    ajax.done(this.onGetElectionsDone.bind(this));
    ajax.fail(this.onFail.bind(this, "Getting elections information"));
};

eLect.prototype.onGetElectionsDone = function(data) {
    this.responses = data;
    console.log(this.responses);
    this.updateViewItems();
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