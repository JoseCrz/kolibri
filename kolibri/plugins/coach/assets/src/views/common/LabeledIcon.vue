<template>

  <span class="wrapper">
    <slot></slot>
    <span class="label">{{ label }}</span>
  </span>

</template>


<script>

  export default {
    name: 'LabeledIcon',
    components: {},
    props: {
      label: {
        type: [String, Number],
        required: true,
      },
    },
  };

</script>


<style lang="scss" scoped>

  .wrapper {
    position: relative;
    margin-right: 16px;
  }

  .label {
    margin-left: 20px;
  }

  .wrapper svg {
    position: absolute;
    top: -1px;
    width: 16px;
  }

</style>
