<template>

  <div>
    <h1>Julie</h1>
    <p>{{ $tr('quizPerformanceLabel', {quiz: 'Some quiz'}) }}</p>
    <HeaderTable>
      <HeaderTableRow>
        <template slot="key">{{ coachStrings.$tr('scoreLabel') }}</template>
        <template slot="value"><Score :value="0.5" /></template>
      </HeaderTableRow>
      <HeaderTableRow>
        <template slot="key">{{ coachStrings.$tr('questionsCorrectLabel') }}</template>
        <template slot="value">{{ coachStrings.$tr('ratio', {value:6, total: 12}) }}</template>
      </HeaderTableRow>
    </HeaderTable>
    <p>{{ coachStrings.$tr('answersLabel') }}</p>
    <p>{{ coachStrings.$tr('attemptsLabel') }}</p>
    <p>{{ coachStrings.$tr('showCorrectAnswerLabel') }}</p>
    <h2>{{ coachStrings.$tr('answersLabel') }}</h2>
    <ul>
      <li><Answer type="noAttempt" /></li>
      <li><Answer type="correct" /></li>
      <li><Answer type="incorrect" /></li>
      <li><Answer type="error" /></li>
      <li><Answer type="hint" /></li>
    </ul>
  </div>

</template>


<script>

  import commonCoach from '../common';

  export default {
    name: 'LearnerQuizReport',
    components: {},
    mixins: [commonCoach],
    $trs: {
      quizPerformanceLabel: "'{quiz}' performance",
    },
  };

</script>


<style lang="scss" scoped></style>
