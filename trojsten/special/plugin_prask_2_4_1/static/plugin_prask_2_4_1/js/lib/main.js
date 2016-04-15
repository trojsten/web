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
            ' je väčšia ako zlúčenina ',
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
            questions: []
        };
    },
    componentDidMount: function componentDidMount() {
        $.getJSON(this.url, function (data) {
            if (data.status == 'Success') {
                this.setState({ questions: data.queries });
            }
        }.bind(this));
    },
    handleReset: function handleReset() {
        $.ajax({
            url: this.url,
            type: 'DELETE',
            dataType: 'json',
            success: function (data) {
                if (data.status == 'Success') {
                    this.setState({ questions: data.queries });
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
        $.post(this.url, { a: this.state.form_a, b: this.state.form_b }, function (data) {
            if (data.status == 'Success') {
                this.setState({ questions: data.queries });
            } else {
                alert(data.message);
            }
        }.bind(this), 'json');
        return true;
    },
    render: function render() {
        var questions = this.state.questions.map(function (item, index) {
            return React.createElement(Question, { key: index, a: item[0], b: item[1] });
        });
        return React.createElement(
            'div',
            null,
            'Odpovede na tvoje doterajšie otázky:',
            React.createElement(
                'ol',
                null,
                questions
            ),
            React.createElement(
                'form',
                { className: 'form form-inline' },
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
                    { type: 'button', className: 'btn btn-primary', onClick: this.handleSubmit },
                    'Porovnaj'
                ),
                React.createElement(
                    'button',
                    { type: 'button', className: 'btn btn-danger', onClick: this.handleReset },
                    'Reset'
                )
            )
        );
    }
});

ReactDOM.render(React.createElement(QuestionList, null), document.getElementById("plugin_prask_2_4_1/questions"));