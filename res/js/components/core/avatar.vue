<template>
    <div class="avatar-wrap" :title="entity.name" :class="{ 'avatar-inline': inline }">
        <div class="avatar" :class="avatarClasses" v-if="entity.avatar !== null">
            <img :src="entity.avatar" alt="">
        </div>
        <div class="avatar avatar-initials" :class="avatarClasses" :data-initials="entity.initials.length" :style="avatarStyle" v-else>
          <span v-if="entity.initials.length <= 4">
            {{ entity.initials }}
          </span>
          <span v-else>
            {{ entity.initials.substr(0, 1) }}...
          </span>
        </div>
    </div>
</template>

<script>
  import { has } from 'lodash'
  import createRandomColor from 'random-color'

  const colorCache = {}

  function randomColorFor (name) {
    const symbol = Symbol.for(String(name))
    if (!has(colorCache, symbol)) {
      colorCache[symbol] = createRandomColor().hexString()
    }
    return colorCache[symbol]
  }

  export default {
    props: {
      entity: Object,
      rounded: Boolean,
      inline: Boolean,
      size: {
        type: Number,
        default: 48
      }
    },
    computed: {
      avatarClasses () {
        return [`avatar-size-${this.size}-${this.size}`, {
          'avatar-circle': this.rounded
        }]
      },
      avatarStyle () {
        return {
          backgroundColor: this.entity.avatar_color || randomColorFor(this.entity.name)
        }
      }
    }
  }
</script>
