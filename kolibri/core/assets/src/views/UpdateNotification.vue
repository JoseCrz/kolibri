<template>

  <KModal
    size="large"
    :submitText="$tr('okButtonLabel')"
    :title="title"
    @submit="submit"
  >
    {{ msg }}
    <KExternalLink
      v-if="linkUrl"
      :href="linkUrl"
      :text="linkText || linkUrl"
    />
    <p v-if="!isSuperuser">{{ $tr('adminMessage') }}</p>
    <KCheckbox
      :label="$tr('hideNotificationLabel')"
      :checked="dontShowNotificationAgain"
      @change="dontShowNotificationAgain = !dontShowNotificationAgain"
    />
  </KModal>

</template>


<script>

  import KExternalLink from 'kolibri.coreVue.components.KExternalLink';
  import KModal from 'kolibri.coreVue.components.KModal';
  import KCheckbox from 'kolibri.coreVue.components.KCheckbox';
  import { mapGetters, mapActions, mapMutations } from 'vuex';

  export default {
    name: 'UpdateNotification',
    components: {
      KCheckbox,
      KExternalLink,
      KModal,
    },
    props: {
      id: {
        type: String,
        required: true,
      },
      title: {
        type: String,
        required: true,
      },
      msg: {
        type: String,
        required: true,
      },
      linkText: {
        type: String,
        required: false,
      },
      linkUrl: {
        type: String,
        required: false,
      },
    },
    data() {
      return {
        dontShowNotificationAgain: false,
      };
    },
    $trs: {
      updateModalHeader: 'Upgrade available',
      adminMessage: 'Please contact the device administrator for this server.',
      okButtonLabel: 'OK',
      hideNotificationLabel: "Don't show this message again",
    },
    computed: {
      ...mapGetters(['isSuperuser']),
    },
    methods: {
      ...mapMutations({
        removeNotification: 'CORE_REMOVE_NOTIFICATION',
      }),
      ...mapActions(['saveDismissedNotification']),
      submit() {
        if (this.dontShowNotificationAgain) {
          this.dontShowNotificationAgain = false;
          this.saveDismissedNotification(this.id);
        }
        this.removeNotification(this.id);
        this.$emit('closeModal');
      },
    },
  };

</script>
