# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""A DataProvider that provides data from a Dataset.

DatasetDataProviders provide data from datasets. The provide can be configured
to use multiple readers simultaneously or read via a single reader.
Additionally, the data being read can be optionally shuffled.

For example, to read data using a single thread without shuffling:

  pascal_voc_data_provider = DatasetDataProvider(
      slim.datasets.pascal_voc.get_split('train'),
      shuffle=False)
  images, labels = pascal_voc_data_provider.Get(['images', 'labels'])

To read data using multiple readers simultaneous with shuffling:

  pascal_voc_data_provider = DatasetDataProvider(
      slim.datasets.pascal_voc.Dataset(),
      num_readers=10,
      shuffle=True)
  images, labels = pascal_voc_data_provider.Get(['images', 'labels'])
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.contrib.slim.python.slim.data import data_provider
from tensorflow.contrib.slim.python.slim.data import parallel_reader


class DatasetDataProvider(data_provider.DataProvider):

  def __init__(self, dataset, num_readers=1, shuffle=True, num_epochs=None,
               common_queue_capacity=256, common_queue_min=128):
    """Creates a DatasetDataProvider.

    Args:
      dataset: An instance of the Dataset class.
      num_readers: The number of parallel readers to use.
      shuffle: Whether to shuffle the data sources and common queue when
        reading.
      num_epochs: The number of times each data source is read. If left as None,
        the data will be cycled through indefinitely.
      common_queue_capacity: The capacity of the common queue.
      common_queue_min: The minimum number of elements in the common queue after
        a dequeue.
    """
    _, data = parallel_reader.parallel_read(
        dataset.data_sources,
        reader_class=dataset.reader,
        num_epochs=num_epochs,
        num_readers=num_readers,
        shuffle=shuffle,
        capacity=common_queue_capacity,
        min_after_dequeue=common_queue_min)

    items = dataset.decoder.list_items()
    tensors = dataset.decoder.decode(data, items)

    super(DatasetDataProvider, self).__init__(
        items_to_tensors=dict(zip(items, tensors)),
        num_samples=dataset.num_samples)
