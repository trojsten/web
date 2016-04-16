'use strict';

var Question = React.createClass({
    displayName: 'Question',

    render: function render() {
        return React.createElement(
            'li',
            null,
            React.createElement(
                'span',
                { className: 'label label-info' },
                this.props.a,
                ' > ',
                this.props.b
            ),
            '  Zlúčenina ',
            React.createElement(
                'em',
                null,
                'č. ',
                this.props.a
            ),
            ' je lepšia ako zlúčenina ',
            React.createElement(
                'em',
                null,
                'č. ',
                this.props.b
            ),
            '.'
        );
    }
});

var QuestionList = React.createClass({
    displayName: 'QuestionList',

    url: '/specialne/prask/2/4/1/api/query/',
    getInitialState: function getInitialState() {
        return {
            form_a: '',
            form_b: '',
            questions: [],
            pending: false
        };
    },
    componentDidMount: function componentDidMount() {
        this.setState({ pending: true });
        $.getJSON(this.url, function (data) {
            if (data.status == 'Success') {
                this.setState({ questions: data.queries, pending: false });
            }
        }.bind(this));
    },
    handleReset: function handleReset() {
        this.setState({ pending: true });
        $.ajax({
            url: this.url,
            type: 'DELETE',
            dataType: 'json',
            success: function (data) {
                if (data.status == 'Success') {
                    this.setState({ questions: data.queries, pending: false });
                }
            }.bind(this)
        });
    },
    handleFormAChange: function handleFormAChange(event) {
        var new_a = event.target.value;
        this.setState({ form_a: new_a });
    },
    handleFormBChange: function handleFormBChange(event) {
        var new_b = event.target.value;
        this.setState({ form_b: new_b });
    },
    handleSubmit: function handleSubmit(event) {
        this.setState({ pending: true });
        $.post(this.url, { a: this.state.form_a, b: this.state.form_b }, function (data) {
            if (data.status == 'Success') {
                this.setState({ questions: data.queries, pending: false });
            } else {
                this.setState({ pending: false });
                alert(data.message);
            }
        }.bind(this), 'json');
        event.stopPropagation();
        event.preventDefault();
    },
    render: function render() {
        var questions;
        if (this.state.questions.length) {
            questions = React.createElement(
                'ol',
                null,
                this.state.questions.map(function (item, index) {
                    return React.createElement(Question, { key: index, a: item[0], b: item[1] });
                })
            );
        } else {
            questions = React.createElement(
                'div',
                { className: 'alert alert-info' },
                'Ešte si nepoložil žiadnu otázku'
            );
        }
        var pending = '';
        if (this.state.pending) {
            pending = React.createElement('span', { className: 'glyphicon glyphicon-refresh glyphicon-animate-rotate pull-right btn btn-link' });
        }
        return React.createElement(
            'div',
            null,
            React.createElement(
                'h2',
                null,
                'Odpovede na tvoje doterajšie otázky:'
            ),
            questions,
            React.createElement(
                'h3',
                null,
                'Nová otázka'
            ),
            React.createElement(
                'form',
                { className: 'form form-inline', onSubmit: this.handleSubmit },
                React.createElement(
                    'label',
                    null,
                    'Porovnaj:'
                ),
                React.createElement('input', { type: 'number', value: this.state.form_a, onChange: this.handleFormAChange,
                    className: 'form-control' }),
                ' a ',
                React.createElement('input', { type: 'number', value: this.state.form_b, onChange: this.handleFormBChange,
                    className: 'form-control' }),
                React.createElement(
                    'button',
                    { type: 'submit', className: 'btn btn-primary' },
                    'Porovnaj'
                ),
                React.createElement(
                    'button',
                    { type: 'button', className: 'btn btn-danger', onClick: this.handleReset },
                    'Reset'
                ),
                pending
            )
        );
    }
});

ReactDOM.render(React.createElement(QuestionList, null), document.getElementById("plugin_prask_2_4_1/questions"));