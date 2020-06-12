// The searchAPI object contains methods for each kind of request we'll make
var EXTERNAL_HOST = "vps-4864b0cc.vps.ovh.net:8000"
var LOCAL_HOST = "localhost:9000"
var HOST = LOCAL_HOST

var EXTERNAL_BIBLE_API_HOST = "http://vps-4864b0cc.vps.ovh.net:8001/bible"
var LOCAL_BIBLE_API_HOST = "http://localhost:8001/bible"
var BIBLE_API_HOST = LOCAL_BIBLE_API_HOST

var searchAPI = {
  searchByTitle: function(query, offset, limit) {
	return $.ajax({
	  url: "http://" + HOST + "/od/articles?q=" 
		+ encodeURIComponent(query) + "&offset=" + offset + "&limit=" + limit,
	  type: "GET",
	  crossDomain: true,
	  contentType: "application/json",
	  dataType: "json"
	});
  },
  getById: function(id, callback) {
		return $.ajax({
		  url: "http://" + HOST + "/od/articles?id=" + id,
		  type: "GET",
		  crossDomain: true,
		  contentType: "application/json",
		  dataType: "json",
		  success: function(data, status, jqXHR) {
				callback(data);
		  }
		});
	},
	getSimilar: function(id, callback){
		return $.ajax({
			url: "http://" + HOST + "/od/articles/similar?id=" + id,
			type: "GET",
			crossDomain: true,
			contentType: "application/json",
			dataType: "json",
			success: function(data, status, jqXHR) {
				callback(data);
			}
		})
  }
};

var bibleReferences = [];

var loadBibleVerses = function(p) {
	var bibleBookMapping = {
		"Facere": "Gen.",
		"Fac.": "Gen.",
		"Genesa": "Gen.",
		"1 Regi": "1 Împ.",
		"2 Regi": "2 Împ.",
		"Judec.": "Jud.",
	};

	var bibleBooks = ["Gen.", "Genesa", "Facere", "Fac.", "Exod", "Levitic", "Numeri", "Iosua",
		 "Jud.", "Judec.", "Rut", "1 Sam.", "1 Samuel", "2 Sam.", "2 Samuel", "Ezra", "Neem.", "Neemia",
		 "Est.", "Estera", "Iov", "Prov.", "Ecles.", "Ier.", "Ierem.", "Ieremia", "Plângeri", "Cânt. Cânt.",
		 "Ezec.",
		 "Osea", "Ioel", "Amos", "Obadia", "Obad.", "Iona", "Mica", "Naum", "Habac.", "Habacuc", "Tef.", "Tefan.",
		 "Tefania", "Hagai", "Zah.", "Zaharia", "Mal.", "Maleahi",
		 "Psalm", "Psalmi", "Ps.", "Deut.", "1 Cronici", "2 Cronici", "1 Împ.", "2 Împ.", "1 Regi", "Isaia",
		 "Daniel",
		 "1 Ioan", "2 Ioan", "3 Ioan", "Matei", "Marcu", "Luca", "Ioan", "Fap. Ap.", 
		 "Fapt. Ap.", "Col.", "Colos.", "Coloseni", "Efes.", "1 Cor.", "2 Cor.", "Rom.", "1 Tes.",
		 "2 Tes.", "Gal.", "Filimon", "Evrei", "Iuda", "1 Tim.", "2 Tim.", "1 Petru", "2 Petru",
		 "Filip.", "Filip", "Iacov", "Tit", "Apoc."];

	bibleBooks.forEach(function(bibleBook){
		var regex = new RegExp("(\\d )*" + bibleBook + "( cap\.)* (\\d+), ?(\\d+)(-\\d+)*((;|și) ?(\\d+), ?(\\d+)(-\\d+)*)*", "ig");
		var newp = p.replace(regex, function(match, bookNumber, unused, cap, verseStart, verseEnd, 
			secondRef, sep, secondCap, secondVerse, secondVerseEnd){
			if (bookNumber)
			{
				return match;
			}

			if (sep)
			{
			}

			if (!verseEnd)
				verseEnd = "";

			if (!secondVerseEnd)
				secondVerseEnd = "";

			if (!secondRef)
			{
				secondRef = "";
			}
			else
			{
				secondRef = "," + secondCap + ":" + secondVerse + secondVerseEnd;
			}

			if (bibleBook in bibleBookMapping)
			{
				bibleBook = bibleBookMapping[bibleBook];
			}

			var bibleReference = bibleBook + " " + cap + ":" + verseStart + verseEnd + secondRef;
			var id = bibleReference.replace(new RegExp('[ .,:-]', 'g'), '_');

			bibleReferences.push({'id': id, 'reference': bibleReference});

			return "<a href='#' class='tooltipLink " + id + "' data-toogle='tooltip' data-html='true'>" 
				+ bibleReference + "</a>";
		});

		if (newp == p && p.indexOf("Fapt. Ap.") != -1)
		{
			//console.log("Couldn't find " + regex + " in " + p);
		}
		else if (newp != p)
		{
			//console.log("Replaced " + bibleBook + "\n in " + p + " \nand got \n" + newp);
			p = newp;
		}
	});
	
	return p;
};

var showItem = function(result) {
	var source = result._source;

  $("#results").hide();
  $("#mainSearchForm").hide();
  $("#backtosearch").show();

  bibleReferences = [];

  var titleTag = $("<h2></h2>").append($('<b></b>').append(source.title));
  var content = $("#contentDiv").html(titleTag);

  var itemSubtitle = $('<h6></h6>').addClass('card-subtitle mt-2 mb-2 text-muted')
		.append("<i>" + source.book + "</i> - " + source.author);
  
  content.append(itemSubtitle);
  content.append($('<br/>'));

  source.verses.forEach(function(verse){
		if (verse === "")
		  content.append($("</br>"));
		else
		{
		  var par = $("</p>").append(loadBibleVerses(verse));
			par.addClass("mb-0");

		  content.append(par);
		}
  });

	bibleReferences.forEach(function(bibleRef){
		var id = bibleRef.id;
  	var ref = bibleRef.reference;
  	var element = $('.' + id);

  	$.ajax({
  			url: BIBLE_API_HOST + "/" + ref,
  			type: "GET",
  			dataType: "jsonp",
  			contentType: "application/json",
  			statusCode: {
  				400: function(){
  					element.attr('title', 'Trimitere invalida: ' + ref + '.');
  					element.tooltip();
  				},
  				404: function(){
  					element.attr('title', 'Nu am găsit versetul ' + ref + '.');
  					element.tooltip();
  				}
  			}
  		}).done(function(response)
  		{
  			var text = "";
  			verses = response.verses.slice(0, 10);
  			verses.forEach(function(verse){
  				text += "<p class='mb-1'> <b>" + verse.name + "</b> - " + verse.text + "</p>";
  			});

  			if (verses.length !== response.verses.length){
  				text += "<p>...</p>";
  			}

  			element.attr('title', text);
  			element.tooltip();
  		});
	});
	  	
  
  content.show();

  searchAPI.getSimilar(result._id, function(response){
  	var articles = response.hits.hits;
  	var needsComma = false;
  	if (response.hits.total.value > 0)
		{
			var par = $('<p></p>').append($('<b></br>').append("Vezi pe aceeași temă: "));
	  	articles.forEach(function(article){
	  		var source = article._source;
			  var title = source.title;

	  		var itemLink = $('<a></a>').prop('href', '#/articles/' + article._id)
	  			.prop('data-toogle', 'tooltip')
	  			.prop('title', source.book + " - " + source.author)
	  			.append(title);

	  		itemLink.click(function(event){
	  			$(this).tooltip('hide');
	  		});

	  		itemLink.tooltip();
	  		if (needsComma)
	  		{
	  			par.append(", ");
	  		}
	  		else
	  		{
	  			needsComma = true;
	  		}

	  		par.append(itemLink);

	  		content.append(par);
	  	});
	  }
  });

  $('.tooltipLink').click(function(event){
  	event.preventDefault();
  	$(this).tooltip();
  });

  window.scrollTo(0,0);
};

var loading = false;
var searchTerm = null;
var index = 1;
var totalHits = 0;

var itemsPerPage = 20;
var itemLimit = itemsPerPage;
var itemOffset = 0;

var search = function(searchTerm, offset, limit){
  searchAPI.searchByTitle(searchTerm, offset, limit).then(function(resp) {
	loading = true;

	var hitsArray = resp.hits.hits;
	totalHits = resp.hits.total.value;

	if (offset == 0)
	{
		var heading;
		if (totalHits == 1)
		{
			heading = $("<h5></h5").append("Am găsit un singur rezultat despre '" 
				+ decodeURIComponent(searchTerm) + "' in " + resp.took + " milisecunde.");	
		}
		else if (totalHits > 0)
		{
			heading = $("<h5></h5").append("Am găsit " + totalHits + " rezultate despre '" 
				+ decodeURIComponent(searchTerm) + "' in " + resp.took + " milisecunde.");
		}
		else
		{
			var heading = $("<h5></h5").append("Nu am găsit rezultate despre '" 
				+ decodeURIComponent(searchTerm) + "'.");
		}
		
		$("#results").append(heading);	
	}	

	hitsArray.forEach(function(eachArticle) {
		  var source = eachArticle._source;

		  var title = source.title;
		  var content = [];

		  var highlight = eachArticle.highlight;
		  if (highlight)
		  {
			if (highlight.hasOwnProperty('title'))
			{
			  title = highlight.title[0];
			}

			if (highlight.hasOwnProperty('verses'))
			{
			  content = highlight.verses;
			} 
	  }

	  var item = $('<div></div>').addClass('card mt-3');
	  var itemBody = $('<div></div>').addClass('card-body p-2');
	  var itemLink = $('<a></a>').prop('href', '#/articles/' + eachArticle._id).append(title);
	  var itemBadge = $('<span></span>').addClass('badge badge-light ml-2').append(source['type']);
	  var itemTitle = $('<h5></h5>').addClass('card-title').append(index + ". ")
		.append(itemLink).append(itemBadge);
	  var itemSubtitle = $('<h6></h6>').addClass('card-subtitle mb-2 text-muted')
		.append("<i>" + source.book + "</i> - " + source.author);

	  itemBody.append(itemTitle).append(itemSubtitle);

	  content.forEach(function(verse){
			itemBody.append($('<p></p>').addClass('mb-0').append(verse));
	  });

	  item.append(itemBody);
	  $("#results").append(item);

	  index ++;
	});

	$("#submitBtn").prop('disabled', false);
	$("#submitBtn").prop('value', 'Search');

	loading=false;
  });
};

var handleSubmit =  function(term) {
  searchTerm = term;

  $("#submitBtn").prop('disabled', true);
  $("#submitBtn").prop('value', 'Searching...');

	$(".ui-menu-item").hide();
  $("#contentDiv").hide();
  $("#results").show();

  $('#results').empty();

  index = 1;
  itemOffset = 0;
  limit = 20;
  var dataSet = [];

  search(term, itemOffset, itemLimit);
  $.router.set('#/search/' + term);
};

$.route('/articles/:id', function(e, params, query){
	searchAPI.getById(params['id'], function(result){
	  showItem(result);
	});
  });

$.route('/search/:q', function(e, params, query){
	if (searchTerm == null && params['q'] != "null")
	{
		handleSubmit(decodeURIComponent(params['q']));
		$("#mainSearch").val(decodeURIComponent(params['q']));
	}
});

$(document).ready(function () {

	$.router.init();

  $("#contentDiv").hide();
  $("#backtosearch").hide();

  $("#link_backtosearch").on('click', function(event){
	event.preventDefault();

	$("#contentDiv").hide();
	$("#backtosearch").hide();    
	$("#results").show();
	$("#mainSearchForm").show();
	$.router.set('#/search/' + searchTerm);
  });
  
  $("#mainSearch").autocomplete({
	source: function(request, response){
	  var term = request.term.toLowerCase();

	  $.ajax({
		url: "http://" + HOST + "/od/titles/completion?prefix=" + encodeURIComponent(term),
		type: "GET",
		crossDomain: true,
		contentType: "application/json",
		dataType: "json",
		success: function(data) {
		  var hits = data['hits']['hits']
		  response($.map(hits, function(hit) {
				return hit;
		  }));
		}
	  });
	},
  }).keyup(function (e) {
		if(e.which === 13) {
			$(".ui-menu-item").hide();
		}            
	}).data("ui-autocomplete")._renderItem = function(ul, item) {
		var source = item._source;

		var itemBookAuthor = $('<span></span>').addClass('ml-2')
			.append("în <i>" + source.book + "</i> - " + source.author);
	return $("<li></li>")
	  .data("item.autocomplete", item._source.title)
	  .append($("<a></a>").attr('href', '#/articles/' + item._id).append($('<b></b>').append(item._source.title))
	  	.append(itemBookAuthor))
	  .appendTo(ul);
  };

  $(document).scroll(function() {
	var bottomOfPage = $(window).scrollTop() + window.innerHeight == $(document).height();

	if(itemOffset < totalHits && searchTerm && !loading && bottomOfPage ) {
	  itemLimit += itemsPerPage;
	  itemOffset += itemsPerPage;
	  search(searchTerm, itemOffset, itemLimit);
	  //alert("Would search for " + searchTerm + ", offset=" + itemOffset + ", limit=" + itemLimit);
	}
  });

// Add event listeners to the submit button
$('#mainSearchForm').submit(function(event){
  event.preventDefault();
  handleSubmit($("#mainSearch").val().trim());
});
});