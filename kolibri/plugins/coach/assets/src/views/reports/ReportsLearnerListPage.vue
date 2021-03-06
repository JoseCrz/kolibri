<template>

  <CoreBase
    :immersivePage="false"
    :appBarTitle="coachStrings.$tr('coachLabel')"
    :authorized="userIsAuthorized"
    authorizedRole="adminOrCoach"
    :showSubNav="true"
  >

    <TopNavbar slot="sub-nav" />

    <div class="new-coach-block">
      <ReportsHeader />
      <KCheckbox :label="coachStrings.$tr('viewByGroupsLabel')" />
      <h2>{{ coachStrings.$tr('overallLabel') }}</h2>
      <CoreTable>
        <thead slot="thead">
          <tr>
            <td>{{ coachStrings.$tr('nameLabel') }}</td>
            <td>{{ coachStrings.$tr('groupsLabel') }}</td>
            <td>{{ coachStrings.$tr('avgQuizScoreLabel') }}</td>
            <td>{{ coachStrings.$tr('exercisesCompletedLabel') }}</td>
            <td>{{ coachStrings.$tr('resourcesViewedLabel') }}</td>
            <td>{{ coachStrings.$tr('lastActivityLabel') }}</td>
          </tr>
        </thead>
        <transition-group slot="tbody" tag="tbody" name="list">
          <tr v-for="tableRow in table" :key="tableRow.id">
            <td>
              <KRouterLink
                :text="tableRow.name"
                :to="classRoute('ReportsLearnerReportPage', { learnerId: tableRow.id })"
              />
            </td>
            <td><TruncatedItemList :items="tableRow.groups" /></td>
            <td><Score :value="tableRow.avgScore" /></td>
            <td>{{ coachStrings.$tr('integer', {value: tableRow.exercises}) }}</td>
            <td>{{ coachStrings.$tr('integer', {value: tableRow.resources}) }}</td>
            <td><ElapsedTime :date="tableRow.lastActivity" /></td>
          </tr>
        </transition-group>
      </CoreTable>
    </div>
  </CoreBase>

</template>


<script>

  import { mapState, mapGetters } from 'vuex';
  import ElapsedTime from 'kolibri.coreVue.components.ElapsedTime';
  import commonCoach from '../common';
  import ReportsHeader from './ReportsHeader';

  export default {
    name: 'ReportsLearnerListPage',
    components: {
      ReportsHeader,
      ElapsedTime,
    },
    mixins: [commonCoach],
    computed: {
      ...mapState('classSummary', ['contentMap']),
      ...mapGetters('classSummary', [
        'groups',
        'lessons',
        'learners',
        'exams',
        'examStatuses',
        'contentStatuses',
      ]),
      table() {
        const sorted = this.dataHelpers.sortBy(this.learners, ['name']);
        const mapped = sorted.map(learner => {
          const groupNames = this.dataHelpers.groupNames(
            this.dataHelpers.map(
              this.groups.filter(group => group.member_ids.includes(learner.id)),
              'id'
            )
          );
          const examStatuses = this.examStatuses.filter(status => learner.id === status.learner_id);
          const contentStatuses = this.contentStatuses.filter(
            status => learner.id === status.learner_id
          );

          const augmentedObj = {
            groups: groupNames,
            avgScore: this.avgScore(examStatuses),
            lessons: undefined,
            exercises: this.exercisesCompleted(contentStatuses),
            resources: this.resourcesViewed(contentStatuses),
            lastActivity: this.lastActivity(examStatuses, contentStatuses),
          };
          Object.assign(augmentedObj, learner);
          return augmentedObj;
        });
        return mapped;
      },
    },
    methods: {
      avgScore(examStatuses) {
        const statuses = examStatuses.filter(status => status.status === this.STATUSES.completed);
        if (!statuses.length) {
          return null;
        }
        return this.dataHelpers.meanBy(statuses, 'score');
      },
      lastActivity(examStatuses, contentStatuses) {
        const statuses = [...examStatuses, ...contentStatuses];
        if (!statuses.length) {
          return null;
        }
        return this.dataHelpers.maxBy(statuses, 'last_activity').last_activity;
      },
      exercisesCompleted(contentStatuses) {
        const statuses = contentStatuses.filter(
          status =>
            this.contentMap[status.content_id].kind === 'exercise' &&
            status.status === this.STATUSES.completed
        );
        return statuses.length;
      },
      resourcesViewed(contentStatuses) {
        const statuses = contentStatuses.filter(
          status =>
            this.contentMap[status.content_id].kind !== 'exercise' &&
            status.status !== this.STATUSES.notStarted
        );
        return statuses.length;
      },
    },
  };

</script>


<style lang="scss" scoped></style>
