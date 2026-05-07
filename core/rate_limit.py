import hashlib
from time import time_ns
from typing import Awaitable

from pyrate_limiter import BucketFactory, Rate, RateItem, RedisBucket


class RedisRateLimitBucketFactory(BucketFactory):
    def __init__(self, rates: list[Rate], redis, key_prefix: str):
        self.rates = rates
        self.redis = redis
        self.key_prefix = key_prefix
        self.buckets = {}

    def wrap_item(self, name: str, weight: int = 1) -> RateItem:
        return RateItem(name, time_ns() // 1_000_000, weight=weight)

    def get(self, item: RateItem) -> Awaitable[RedisBucket] | RedisBucket:
        bucket_key = self.get_bucket_key(item.name)
        bucket = self.buckets.get(bucket_key)
        if bucket:
            return bucket

        async def create_bucket():
            bucket = await RedisBucket.init(self.rates, self.redis, bucket_key)
            self.buckets[bucket_key] = bucket
            self.schedule_leak(bucket)
            return bucket

        return create_bucket()

    def get_bucket_key(self, name: str) -> str:
        key_hash = hashlib.sha256(name.encode("utf-8")).hexdigest()
        return f"{self.key_prefix}:{key_hash}"
