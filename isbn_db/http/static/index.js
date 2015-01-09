$.ajaxSettings.traditional = true;

App = {};
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
	current_page: -1,
	params: {},
	model: Backbone.Model.extend({idAttribute: '_id'}),
	
	initialize: function() {
		this.container = $('.books');
		
		this.on('add', _.bind(function(model) {
			model.view = new App.Views.Book({model: model});
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
			url: '/books' + '?' + $.param({page: this.current_page, q: this.q}),
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
		this.q = q;
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
		if (evt.keyCode == 13 || App.books.q != this.$el.val()) {
			App.books.search(this.$el.val());
		}
	}
});

App.Views.Form = Backbone.View.extend({
	events: {
		'submit': 'submit'
	},
	
	submit: function(evt) {
		var btn = this.$('button[type=submit]');
		btn.removeClass('btn-success btn-danger');
		btn.addClass('btn-warning disabled');
		
		$.ajax({
			type: 'POST',
			url: this.action,
			data: this.data(),
		}).done(_.bind(function(data, status) {
			if(this.done) this.done(data);
			btn.addClass('btn-success');
		}, this)).fail(function() {
			console.log(arguments);
			btn.text('Error!');
			btn.addClass('btn-danger');
		}).always(function() {
			btn.removeClass('btn-warning disabled');
		});
		return false;
	}
});

App.Views.AddBookForm = App.Views.Form.extend({
	el: '#add-book',
	action: 'books',
	
	data: function() {
		return {
			title: this.$('input[name=title]').val(),
			authors: this.$('input[name=authors]').val().split(','),
			identifiers: this.$('input[name=identifiers]').val().split(','),
		};
	},
	
	done: function(data) {
		App.books.add(data, {merge: true});
	}
});

App.Views.AddISBNForm = App.Views.Form.extend({
	el: '#add-isbn',
	action: 'isbns',
	
	data: function() {
		return {
			start: this.$('input[name=start]').val(),
			end: this.$('input[name=end]').val(),
		};
	}
});


$(document).ready(function() {
	App.books = new App.Collections.Books();
	App.search_bar = new App.Views.SearchBar();
	App.add_book_form = new App.Views.AddBookForm();
	App.add_isbn_form = new App.Views.AddISBNForm();
	
	App.books.load_next_page();
	$(window).scroll(function(){
		if ($(window).scrollTop() >= $(document).height() - $(window).height() - 200) {
			App.books.load_next_page();
		}
	});
	
	App.events = new EventSource('/events');
	App.events.addEventListener('log', function(evt) {
		$('#logs').prepend(JSON.parse(evt.data).replace('<', '&lt;').replace('>', '&gt;') + '\n');
	});
});
