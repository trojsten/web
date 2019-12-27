const React = require('react');
const ReactDOM = require('react-dom');

var Question = React.createClass({
  render: function () {
    return (
      <li>
        <span className="label label-info">
          {`${this.props.a} < ${this.props.b}`}
        </span>
        &nbsp; Guľôčka <em>č. {this.props.a}</em> je ľahšia ako guľôčka <em>č. {this.props.b}</em>.
      </li>
    );
  }
});

var QuestionList = React.createClass({
  url: '/specialne/prask/2/4/1/api/query/',
  getInitialState: function () {
    return {
      form_a: '',
      form_b: '',
      questions: [],
      pending: false
    }
  },
  componentDidMount: function () {
    this.setState({pending:true});
    $.getJSON(this.url, function (data) {
      if (data.status == 'Success') {
        this.setState({questions: data.queries, pending: false});
      }
    }.bind(this));
  },
  handleReset: function () {
    this.setState({pending:true});
    $.ajax({
      url: this.url,
      type: 'DELETE',
      dataType: 'json',
      success: function (data) {
        if (data.status == 'Success') {
          this.setState({questions: data.queries, pending: false});
        }
      }.bind(this)
    });
  },
  handleFormAChange: function (event) {
    var new_a = event.target.value;
    this.setState({form_a: new_a});
  },
  handleFormBChange: function (event) {
    var new_b = event.target.value;
    this.setState({form_b: new_b});
  },
  handleSubmit: function (event) {
    this.setState({pending: true});
    $.post(
      this.url,
      {a: this.state.form_a, b: this.state.form_b},
      function (data) {
        if (data.status == 'Success') {
          this.setState({questions: data.queries, pending: false});
        } else {
          this.setState({pending: false});
          alert(data.message);
        }
      }.bind(this), 'json');
    event.stopPropagation();
    event.preventDefault();
  },
  render: function () {
    var questions;
    if (this.state.questions.length) {
      questions = <ol>{this.state.questions.map(function (item, index) {
        return <Question key={index} a={item[0]} b={item[1]}/>;
      })}</ol>;
    } else {
      questions = <div className="alert alert-info">Ešte si nepoložil žiadnu otázku</div>
    }
    var pending = '';
    if (this.state.pending) {
      pending = <span className="glyphicon glyphicon-refresh glyphicon-animate-rotate pull-right btn btn-link"/>;
    }
    return <div>
      <h2>Odpovede na tvoje doterajšie otázky:</h2>
      {questions}
      <h3>Nová otázka</h3>
      <form className="form form-inline" onSubmit={this.handleSubmit}>
        <label>Porovnaj:</label>
        <input type="number" value={this.state.form_a} onChange={this.handleFormAChange}
             className="form-control"/>
        &nbsp;a&nbsp;
        <input type="number" value={this.state.form_b} onChange={this.handleFormBChange}
             className="form-control"/>
        <button type="submit" className="btn btn-primary">Porovnaj</button>
        <button type="button" className="btn btn-danger" onClick={this.handleReset}>Reset</button>
        {pending}
      </form>
    </div>;
  }
});

ReactDOM.render(
  <QuestionList />, document.getElementById("plugin_prask_2_4_1/questions")
);
