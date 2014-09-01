App = {};
App.auto_refresh = true;
App.Collections = {};
App.Views = {};

App.Views.Book = Backbone.View.extend({
	constructor: function() {
		Backbone.View.prototype.constructor.apply(this, arguments);
		this.template = Handlebars.compile($('#book-template').html());
		this.model.on('change', _.bind(this.render, this));
		this.render();
	},
	render: function(append) {
		var html = this.template(this.model.attributes);
		var old_el = this.$el;
		this.setElement(html);
		old_el.replaceWith(this.$el);
	}
});

App.Collections.Books = Backbone.Collection.extend({
	url: 'books',
	current_page: -1,
	params: {},
	
	initialize: function() {
		this.container = $('.books');
		
		this.on('add', _.bind(function(model) {
			model.view = new App.Views.Book({model: model});
			model.view.$('*[data-toggle="tooltip"]').tooltip();
			this.container.append(model.view.$el);
		}, this));
	},

	load_next_page: function(page) {
		if (this.loading) {
			return;
		}

		this.current_page++;
		this.loading = true;
		
		$.ajax({
			type: 'GET',
			url: '/' + this.url + '?' + $.param(_.extend({page: this.current_page}, this.params)),
			context: this
		}).done(function(data, status) {
			if (this.current_page == 0) {
				this.container.html('');
				this.reset();
			}
			this.add(data);
			this.loading = false;
		});
	},
	
	search: function(q) {
		if (q) {
			this.url = 'search';
			this.params.q = q;
		}
		else {
			this.url = 'books';
			this.params = {};
		}
		this.current_page = -1;
		this.load_next_page();
	}
});

App.Views.SearchBar = Backbone.View.extend({
	el: '.search input',
	events: {
		'keyup': 'keyup',
	},

	keyup: function(evt) {
		evt.preventDefault();
		if (evt.keyCode == 13 || App.books.params.q != this.$el.val()) {
			App.books.search(this.$el.val());
		}
	}
});

App.Views.Logs = Backbone.View.extend({
	REFRESH_INTERVAL: 1000,
	el: '#logs',
	
	refresh: function() {
		$.ajax({
			type: 'GET',
			url: '/logs',
			context: this
		}).done(function(data, status) {
			this.$('.loading').hide();
			this.$('.data').removeClass('hidden');
			this.$('.data').text(data.join("\n"));
		}).always(function() {
			if (App.auto_refresh) {
				setTimeout(_.bind(this.refresh, this), this.REFRESH_INTERVAL);
			}
		});
	}
});


$(document).ready(function() {
	App.logs = new App.Views.Logs();
	App.books = new App.Collections.Books();
	App.search_bar = new App.Views.SearchBar();
	
	App.logs.refresh();
	
	App.books.load_next_page();
	$(window).scroll(function(){
		if ($(window).scrollTop() >= $(document).height() - $(window).height() - 200) {
			App.books.load_next_page();
		}
	});
});


if ('auto_refresh' in localStorage) {
	App.auto_refresh = (localStorage['auto_refresh'] == 'true');
}
App.set_auto_refresh = function(val) {
	localStorage['auto_refresh'] = val;
	App.auto_refresh = val;
}
