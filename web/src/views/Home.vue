<template>
  <v-container>
    <Container>
      <v-img class="mx-auto my-12" max-width="400" alt="LGTM logo" src="@/assets/logo.png"></v-img>
    </Container>

    <Section>
      <template v-slot:title>Welcome to LGTM</template>
      <p>
        <a href="https://dev.to/meseta/lgtm-devlog-0-teaching-git-through-playing-a-game-381j">Find out more here!</a>
      </p>
    </Section>
  </v-container>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator';
import Section from '@/components/Section.vue'
import Container from '@/components/Container.vue'

@Component({ components: { Section, Container } })
export default class HomeView extends Vue {}
</script>
